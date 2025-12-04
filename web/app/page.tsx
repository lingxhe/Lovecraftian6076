"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { ChevronDown } from "lucide-react";
import { useRouter } from "next/navigation";
import { SparklesCore } from "./ui/sparkles";

interface Book {
  id: string;
  title: string;
  isAvailable: boolean;
}

const BOOKS: Book[] = [
  {
    id: "alone-against-flames",
    title: "Alone Against the Flames",
    isAvailable: true,
  },
  {
    id: "coming-soon-1",
    title: "Coming Soon",
    isAvailable: false,
  },
  {
    id: "coming-soon-2",
    title: "Coming Soon",
    isAvailable: false,
  },
  {
    id: "coming-soon-3",
    title: "Coming Soon",
    isAvailable: false,
  },
];

export default function HomePage() {
  const router = useRouter();
  const [bookOpened, setBookOpened] = useState(false);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [showSynopsis, setShowSynopsis] = useState(false);
  const [galleryCollapsed, setGalleryCollapsed] = useState(false);
  const [diceRotation, setDiceRotation] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setDiceRotation(window.scrollY * 0.2);
    };
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleBookClick = (bookId: string) => {
    const book = BOOKS.find((b) => b.id === bookId);
    if (book && book.isAvailable) {
      setSelectedBookId(bookId);
      setBookOpened(true);
      setShowSynopsis(false);
      setGalleryCollapsed(false);
      setTimeout(() => setGalleryCollapsed(true), 400);
      setTimeout(() => setShowSynopsis(true), 800);
    }
  };

  const handleReturnToGallery = () => {
    setBookOpened(false);
    setSelectedBookId(null);
    setShowSynopsis(false);
    setGalleryCollapsed(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white overflow-x-hidden">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 animate-background-fade-in">
          <Image
            src="/lib/pic/monster-cthulhu-wallpaper-2560x1080_14.jpg"
            alt="Cthulhu Wallpaper"
            fill
            className="object-cover"
            priority
            quality={90}
          />
          <div className="absolute inset-0 bg-black/60 animate-overlay-fade-in" />
        </div>

        <div className="relative z-10 text-center space-y-6 animate-title-slide-in">
          <h1
            className="text-8xl md:text-[12rem] font-bold tracking-tight animate-title-shadow-flicker"
            style={{
              fontFamily: "var(--font-metal-mania), serif",
              background:
                "linear-gradient(to bottom, rgb(211, 7, 7) 0%, rgb(168, 4, 4) 25%, rgb(126, 14, 14) 50%, rgb(77, 3, 3) 75%, rgb(19, 0, 0) 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              textShadow: "none",
              animationDelay: "1s",
            }}
          >
            Lovecraftian
          </h1>
          <h2
            className="text-6xl md:text-9xl tracking-wider animate-title-shadow-flicker"
            style={{
              fontFamily: "var(--font-metal-mania), serif",
              color: "#cbd5e1",
              textShadow: "none",
              animationDelay: "1s",
            }}
          >
            Language Mode
          </h2>
          <div className="pt-12 animate-bounce">
            <ChevronDown
              className="w-8 h-8 mx-auto text-emerald-300 drop-shadow-lg"
              style={{
                filter: "drop-shadow(0 0 10px rgba(16, 185, 129, 0.6))",
              }}
            />
          </div>
          <div className="mt-10 flex justify-center">
            <div className="p-3 rounded-full border border-emerald-200/60 shadow-[0_0_25px_rgba(16,185,129,0.35)] bg-black/30 backdrop-blur-sm">
              <Image
                src="/lib/pic/d20.png"
                alt="D20 Icon"
                width={90}
                height={90}
                className="drop-shadow-[0_0_25px_rgba(16,185,129,0.5)] animate-pulse"
                style={{
                  filter: "invert(1) brightness(1.2)",
                  transform: `rotate(${diceRotation}deg)`,
                  transition: "transform 0.1s linear",
                }}
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* Book Section */}
      <section className="min-h-screen flex items-center justify-center relative py-36">
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/60 via-emerald-950/75 to-slate-950/90 backdrop-blur-[2px]" />
          <div className="w-full absolute inset-0 h-screen">
            <SparklesCore
              id="tsparticlesfullpage"
              background="transparent"
              minSize={0.6}
              maxSize={2}
              speed={2}
              particleDensity={50}
              className="w-full h-full"
              particleColor="#FFFFFF"
            />
          </div>
          {bookOpened && selectedBookId === "alone-against-flames" && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="relative w-[60vw] max-w-3xl aspect-[3/4] opacity-0 animate-book-backdrop-in">
                <Image
                  src="/lib/pic/book.jpg"
                  alt="Book Backdrop"
                  fill
                  className="object-cover rounded-3xl shadow-[0_0_80px_rgba(0,0,0,0.6)] transition duration-700"
                />
                <div className="absolute inset-0 rounded-3xl bg-slate-950/35" />
              </div>
            </div>
          )}
        </div>

        <div className="relative w-full max-w-7xl mx-auto px-6 pb-[22rem] lg:pb-1">
          <div
            className={[
              "books-gallery relative z-10",
              bookOpened ? "books-gallery-active" : "",
              galleryCollapsed ? "books-gallery-collapse" : "",
            ]
              .filter(Boolean)
              .join(" ")}
          >

            {BOOKS.map((book) => (
              <div
                key={book.id}
                className={`books__item ${
                  bookOpened
                    ? selectedBookId === book.id
                      ? "books__item-active"
                      : "books__item-hidden"
                    : ""
                }`}
              >
                <div className="books__container">
                  <div className="books__back-cover"></div>
                  <div className="books__inside">
                    <div className="books__page"></div>
                    <div className="books__page"></div>
                    <div className="books__page"></div>
                  </div>
                  <div className="books__cover">
                    <div
                      className={`books__image rounded-lg shadow-2xl border-4 ${
                        book.id === "alone-against-flames"
                          ? "border-amber-950"
                          : "border-slate-950"
                      } overflow-hidden relative`}
                      style={{ minHeight: "320px" }}
                    >
                      {book.id === "alone-against-flames" ? (
                        <>
                          <Image
                            src="/lib/pic/book.jpg"
                            alt="Alone Against the Flames"
                            fill
                            className="object-cover"
                            priority
                          />
                          <div className="books__overlay">
                            <div className="text-center space-y-3">
                              <p className="text-xs uppercase tracking-[0.4em] text-amber-200/70">
                                Interactive Solo Scenario
                              </p>
                              <h3 className="text-2xl font-bold text-amber-100 drop-shadow-lg">
                                Alone Against
                              </h3>
                              <h3 className="text-2xl font-bold text-amber-100 drop-shadow-lg -mt-2">
                                the Flames
                              </h3>
                              {!bookOpened && (
                                <p className="text-amber-200 text-xs mt-4 animate-pulse drop-shadow-lg">
                                  Click to open
                                </p>
                              )}
                            </div>
                          </div>
                        </>
                      ) : (
                        <>
                          <Image
                            src="/lib/pic/othercover.png"
                            alt="Coming Soon"
                            fill
                            className="object-cover"
                          />
                          <div className="books__overlay bg-black/40">
                            <div className="text-center space-y-2">
                              <p className="text-sm uppercase tracking-[0.4em] text-slate-300/70">
                                Mythos Series
                              </p>
                              <h3 className="text-xl font-bold text-slate-100 drop-shadow-lg">
                                Coming Soon
                              </h3>
                            </div>
                          </div>
                        </>
                      )}
                      <div className="books__effect"></div>
                      <div className="books__light"></div>
                    </div>
                    {book.isAvailable && (
                      <div
                        className="books__hitbox"
                        onClick={() => !bookOpened && handleBookClick(book.id)}
                      ></div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

  {bookOpened && selectedBookId === "alone-against-flames" && showSynopsis && (
    <div className="absolute inset-x-0 top-full -mt-24 flex justify-center px-6 z-20 mb-48">
      <div className="w-full max-w-3xl bg-slate-900/80 border border-amber-900 rounded-3xl p-8 lg:p-10 shadow-[0_0_60px_rgba(8,7,5,0.8)] animate-book-synopsis mb-24">
        <div className="space-y-6 text-amber-100">
          <div>
            <p className="text-sm uppercase tracking-widest text-amber-400">Interactive Solo Scenario</p>
            <h3 className="text-4xl font-bold mt-2">Alone Against the Flames</h3>
            <p className="text-amber-200/80 mt-1">By Chaosium Inc.</p>
          </div>
          <div className="space-y-4 text-lg leading-relaxed text-amber-50/90">
            <p>
              <span className="font-semibold text-amber-200">Timeline:</span> A sweltering summer in the 1920s. You are an ordinary traveler bound for Arkham (profession optional: professor, doctor, journalist, etc.).
            </p>
            <p>
              <span className="font-semibold text-amber-200">Opening Scene:</span> Your long-distance taxi breaks down, diverting you to a remote village where a sinister ritual is quietly taking shape.
            </p>
            <p className="italic text-amber-100">
              Prepare your investigator and step into the unknown. Every choice could draw you closer to the truth—or to madness.
            </p>
          </div>
          <button
            onClick={() => router.push("/create-character")}
            className="w-full mt-4 px-6 py-3 bg-amber-700 text-amber-50 rounded-xl hover:bg-amber-600 transition-colors font-semibold tracking-wide"
          >
            Start Your Adventure
          </button>
          <button
            onClick={handleReturnToGallery}
            className="w-full mt-3 px-6 py-3 border border-amber-700 text-amber-200 rounded-xl hover:bg-amber-900/40 transition-colors font-semibold tracking-wide"
          >
            Back to Gallery
          </button>
        </div>
      </div>
    </div>
  )}
        </div>
      </section>
    </div>
  );
}

