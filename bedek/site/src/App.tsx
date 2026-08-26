import { Nav } from "./components/Nav";
import { Footer } from "./components/Footer";
import { Consent } from "./components/Consent";
import { Hero } from "./sections/Hero";
import { Apps, Contact, Faq, Features, How, Problem } from "./sections/Body";

export default function App() {
  return (
    <>
      <a className="skip" href="#main">
        דילוג לתוכן
      </a>
      <Nav />
      <main id="main">
        <Hero />
        <Problem />
        <How />
        <Features />
        <Apps />
        <Faq />
        <Contact />
      </main>
      <Footer />
      <Consent />
    </>
  );
}
