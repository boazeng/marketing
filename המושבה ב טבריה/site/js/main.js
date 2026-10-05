(function () {
  "use strict";

  var cfg = window.SITE_CONFIG || {};

  /* ---------- Meta pixel ---------- */
  // Loaded from here rather than the <head> so one config value turns it on
  // and off. track() is a no-op until the pixel exists, so an ad blocker or
  // an empty id never breaks the form.
  var pixelId = (cfg.metaPixelId || "").trim();
  if (pixelId && !window.fbq) {
    (function (f, b, e, v, n, t, s) {
      n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n;
      n.push = n; n.loaded = true; n.version = "2.0"; n.queue = [];
      t = b.createElement(e); t.async = true; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", pixelId);
    window.fbq("track", "PageView");
  }
  function track(event, params) {
    if (window.fbq) window.fbq("track", event, params || {});
  }

  /* ---------- Sticky header shadow ---------- */
  var header = document.getElementById("site-header");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 12);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile nav ---------- */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
      });
    });
  }

  /* ---------- Smooth scroll for in-page anchors ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href");
      if (!id || id === "#") return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  /* ---------- WhatsApp ---------- */
  var waNumber = (cfg.whatsappNumber || "").replace(/\D/g, "");
  // "המושבה ב׳" in this text is how the shared WhatsApp number knows which
  // campaign a message belongs to -- keep the project name in it.
  var defaultWaMsg =
    "שלום, אשמח לקבל פרטים על קרקע למגורים במושבה ב׳ בטבריה (תכנית מאושרת).";

  function buildWaUrl(message) {
    if (!waNumber) return null;
    var base = "https://wa.me/" + waNumber;
    if (message) base += "?text=" + encodeURIComponent(message);
    return base;
  }

  document.querySelectorAll("[data-whatsapp]").forEach(function (el) {
    var url = buildWaUrl(defaultWaMsg);
    if (!url) {
      // No number configured: a button that does nothing is worse than none.
      el.hidden = true;
      return;
    }
    el.href = url;
    el.target = "_blank";
    el.rel = "noopener";
    el.addEventListener("click", function () {
      track("Contact", { content_name: "moshava-b", method: "whatsapp" });
    });
  });

  /* ---------- Lead form ---------- */
  var form = document.getElementById("lead-form");
  var statusEl = document.getElementById("form-status");

  function showStatus(msg, ok) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = "form-status " + (ok ? "ok" : "err");
  }

  function validatePhone(phone) {
    var digits = phone.replace(/\D/g, "");
    return digits.length >= 9 && digits.length <= 12;
  }

  /* utm_* / gclid / fbclid off the URL, so a lead can be traced to the ad
     that paid for it. Read once, at load: the query is gone after an in-page
     anchor click. */
  var campaign = {};
  try {
    new URLSearchParams(location.search).forEach(function (v, k) {
      if (k.indexOf("utm_") === 0 || k === "gclid" || k === "fbclid") campaign[k] = v;
    });
  } catch (err) { /* old browser: the lead still goes, untagged */ }
  var startedAt = Date.now();

  function buildPrefill(p) {
    var lines = [
      "פנייה מדף נחיתה — המושבה ב׳",
      "שם: " + p.name,
      "טלפון: " + p.phone
    ];
    if (p.note) lines.push("הערה: " + p.note);
    return lines.join("\n");
  }

  /* The confirmation takes the form's place, so the visitor is left in no
     doubt that the details arrived. */
  function showDone(name) {
    var done = document.getElementById("form-done");
    if (!done) {
      showStatus("הפרטים התקבלו. תודה שפניתם — נחזור אליכם בהקדם.", true);
      return;
    }
    var first = (name || "").split(/\s+/)[0];
    var nameEl = document.getElementById("form-done-name");
    if (nameEl && first) nameEl.textContent = first + ", ";
    form.hidden = true;
    done.hidden = false;
    done.scrollIntoView({ block: "center", behavior: "smooth" });
    done.focus({ preventScroll: true });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      showStatus("", true);

      var name = (form.name.value || "").trim();
      var phone = (form.phone.value || "").trim();
      var note = (form.note.value || "").trim();

      if (name.length < 2) {
        showStatus("נא להזין שם מלא.", false);
        form.name.focus();
        return;
      }
      if (!validatePhone(phone)) {
        showStatus("נא להזין מספר טלפון תקין.", false);
        form.phone.focus();
        return;
      }

      var payload = {
        name: name,
        phone: phone,
        note: note,
        // The lead proxy is shared by every TACT site; this is how the lead
        // is filed under the right project in TACT Task.
        project: "moshava-b",
        source: "landing",
        page: location.href,
        referrer: document.referrer || "",
        campaign: campaign,
        // Both are bot checks the proxy applies: a field no person sees, and
        // a form "filled" faster than a person can type.
        website: form.website ? form.website.value : "",
        startedAt: startedAt
      };

      var endpoint = (cfg.formEndpoint || "").trim();

      if (endpoint) {
        var submitBtn = form.querySelector('[type="submit"]');
        var submitLabel = submitBtn ? submitBtn.textContent : "";
        if (submitBtn) {
          submitBtn.disabled = true;
          // The first send after a quiet hour takes a few seconds; without
          // this the button just looks dead and people press it again.
          submitBtn.textContent = "שולח…";
        }
        fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        })
          .then(function (res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            track("Lead", { content_name: "moshava-b" });
            form.reset();
            showDone(name);
          })
          .catch(function () {
            showStatus("שליחה נכשלה. נסו שוב או פנו בוואטסאפ.", false);
            var wa = buildWaUrl(buildPrefill(payload));
            if (wa) window.open(wa, "_blank", "noopener");
          })
          .finally(function () {
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.textContent = submitLabel;
            }
          });
        return;
      }

      // No endpoint: WhatsApp carries the lead. Never show "received" when
      // nothing was sent anywhere -- that is a lead lost with a thank-you.
      var waUrl = buildWaUrl(buildPrefill(payload));
      if (waUrl) {
        window.open(waUrl, "_blank", "noopener");
        showStatus("נפתח וואטסאפ עם הפרטים שלכם. שלחו את ההודעה להשלמת הפנייה.", true);
        form.reset();
      } else {
        showStatus("לא ניתן לשלוח כרגע. נסו שוב מאוחר יותר.", false);
      }
    });
  }

  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
