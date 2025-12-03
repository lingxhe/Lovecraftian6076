"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Dice1, Save, Upload, X } from "lucide-react";
import { useStore, Character } from "@/store/useStore";

const AVATAR_OPTIONS = [
  "🧑‍🔬",
  "🧑‍🎓",
  "🧑‍⚕️",
  "🧑‍🏫",
  "🧑‍💼",
  "🧑‍🔧",
  "🧙",
  "🕵️",
  "👮",
  "🎩",
  "👤",
  "🧛",
];

export default function CreateCharacterPage() {
  const router = useRouter();
  const { character, setCharacter } = useStore();
  const isCustomAvatar = character?.avatar?.startsWith("data:image") ?? false;
  const [selectedAvatar, setSelectedAvatar] = useState(
    isCustomAvatar && character ? character.avatar : character?.avatar || "🧑‍🔬"
  );
  const [customAvatar, setCustomAvatar] = useState<string | null>(
    isCustomAvatar && character ? character.avatar : null
  );
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState(character?.name || "");
  const [str, setStr] = useState(character?.str || 60);
  const [intAttr, setIntAttr] = useState(character?.int || 60);
  const [pow, setPow] = useState(character?.pow || 60);
  const [spot, setSpot] = useState(character?.spot || 50);
  const [listen, setListen] = useState(character?.listen || 50);
  const [stealth, setStealth] = useState(character?.stealth || 50);
  const [charm, setCharm] = useState(character?.charm || 50);
  const [backgroundStory, setBackgroundStory] = useState(character?.background_story || "");

  const [luckRolls, setLuckRolls] = useState<number[]>([]);
  const [rollCount, setRollCount] = useState(0);
  const [bestLuck, setBestLuck] = useState(character?.luck || 50);

  const coreTotal = str + intAttr + pow;
  const skillBudget = intAttr * 4;
  const skillUsed = spot + listen + stealth + charm;
  const san = pow;

  const rollLuck = () => {
    if (rollCount >= 3) return;
    const dice = Array.from({ length: 3 }, () => Math.floor(Math.random() * 6) + 1);
    const result = dice.reduce((sum, value) => sum + value, 0) * 5;
    const newRolls = [...luckRolls, result];
    setLuckRolls(newRolls);
    setRollCount((prev) => prev + 1);
    // Always set bestLuck to the maximum value from all rolls
    const maxRoll = Math.max(...newRolls);
    setBestLuck(maxRoll);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check if file is an image
    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      return;
    }

    // Check file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      alert("Image size should be less than 2MB.");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      setCustomAvatar(base64String);
      setSelectedAvatar(base64String);
    };
    reader.onerror = () => {
      alert("Failed to read the image file.");
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveCustomAvatar = () => {
    setCustomAvatar(null);
    setSelectedAvatar("🧑‍🔬");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSave = () => {
    const errors: string[] = [];
    if (!name.trim()) errors.push("Please enter a name before saving.");
    if (coreTotal > 180) errors.push(`Core attributes total (${coreTotal}) exceeds 180.`);
    if (skillUsed > skillBudget) errors.push(`Skill points used (${skillUsed}) exceeds budget (${skillBudget}).`);
    if (rollCount === 0) errors.push("Please roll LUCK at least once before saving.");

    if (errors.length) {
      alert(errors.join("\n"));
      return;
    }

    const newCharacter: Character = {
      name: name.trim(),
      str,
      int: intAttr,
      pow,
      spot,
      listen,
      stealth,
      charm,
      luck: bestLuck,
      san,
      avatar: customAvatar || selectedAvatar,
      background_story: backgroundStory.trim(),
    };

    setCharacter(newCharacter);
    router.push("/chat");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white overflow-x-hidden">
      <section className="min-h-screen py-20">
        <div className="max-w-6xl mx-auto px-6 space-y-8">
          {/* Module Synopsis */}
          <div className="w-full max-w-4xl mx-auto bg-slate-900/80 border border-amber-900 rounded-3xl p-8 lg:p-10 shadow-[0_0_60px_rgba(8,7,5,0.8)]">
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
            </div>
          </div>

          <header className="text-center space-y-4">
            <p className="text-sm uppercase tracking-wider text-slate-400">Call of Cthulhu Solo</p>
            <h1 className="text-4xl font-bold">Create Character</h1>
            <p className="text-slate-300 mt-3">
              Set up your CoC investigator. All information is saved locally in your browser.
            </p>
          </header>

        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-1">Image Selection</h2>
            <p className="text-sm text-slate-400">Choose an emoji or upload your own avatar</p>
          </div>

          {/* Custom Avatar Upload */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-slate-300">Custom Avatar</label>
            {customAvatar ? (
              <div className="relative inline-block">
                <div className="relative w-24 h-24 rounded-xl overflow-hidden border-2 border-indigo-400 bg-indigo-500/20">
                  <img
                    src={customAvatar}
                    alt="Custom avatar"
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={handleRemoveCustomAvatar}
                    className="absolute top-1 right-1 w-6 h-6 rounded-full bg-red-600 hover:bg-red-700 flex items-center justify-center text-white text-xs transition-colors"
                    title="Remove custom avatar"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
                <p className="text-xs text-slate-400 mt-2">Custom avatar selected</p>
              </div>
            ) : (
              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="avatar-upload"
                />
                <label
                  htmlFor="avatar-upload"
                  className="flex items-center justify-center gap-2 w-full max-w-xs px-6 py-4 rounded-xl border-2 border-dashed border-slate-700 hover:border-indigo-500 bg-slate-800/50 hover:bg-slate-800 cursor-pointer transition-all"
                >
                  <Upload className="w-5 h-5 text-slate-400" />
                  <span className="text-slate-300 font-medium">Upload Image</span>
                </label>
                <p className="text-xs text-slate-500 mt-2">Max 2MB, JPG/PNG/GIF</p>
              </div>
            )}
          </div>

          {/* Emoji Options */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-slate-300">Emoji Options</label>
            <div className="grid grid-cols-6 gap-4">
              {AVATAR_OPTIONS.map((emoji) => (
                <button
                  key={emoji}
                  onClick={() => {
                    setSelectedAvatar(emoji);
                    setCustomAvatar(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                  className={`p-4 rounded-xl border transition-all ${
                    !customAvatar && selectedAvatar === emoji
                      ? "border-indigo-400 bg-indigo-500/20 scale-105"
                      : "border-slate-700 hover:border-slate-500"
                  }`}
                >
                  <div className="text-5xl">{emoji}</div>
                  <p className="mt-2 text-xs text-slate-400">
                    {!customAvatar && selectedAvatar === emoji ? "Selected" : "Select"}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-xl font-semibold">LUCK</h2>
              <p className="text-sm text-slate-400 mt-1">Roll 3d6×5 (up to 3 times, keep the best result)</p>
            </div>
            <button
              onClick={rollLuck}
              disabled={rollCount >= 3}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 disabled:cursor-not-allowed transition-all font-semibold shadow-lg hover:shadow-indigo-500/50 disabled:shadow-none"
            >
              <Dice1 className="w-5 h-5" />
              {rollCount >= 3 ? "No Rolls Left" : `Roll LUCK (${3 - rollCount} left)`}
            </button>
          </div>

          {luckRolls.length > 0 && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {luckRolls.map((value, idx) => (
                  <div
                    key={idx}
                    className={`relative rounded-xl p-4 border-2 transition-all ${
                      value === bestLuck
                        ? "bg-emerald-900/40 border-emerald-500 shadow-lg shadow-emerald-500/30 scale-105"
                        : "bg-slate-800/60 border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-slate-400">Roll {idx + 1}</span>
                      {value === bestLuck && (
                        <span className="text-xs bg-emerald-500 text-white px-2 py-1 rounded-full font-semibold">
                          Best
                        </span>
                      )}
                    </div>
                    <p className="text-3xl font-bold text-slate-100">{value}</p>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-900/30 to-emerald-800/20 border border-emerald-700/50 rounded-xl">
                <span className="text-slate-300 font-medium">Final LUCK Value:</span>
                <span className="text-2xl font-bold text-emerald-300">{bestLuck}</span>
              </div>
            </div>
          )}

          {luckRolls.length === 0 && (
            <div className="text-center py-8 text-slate-400 border-2 border-dashed border-slate-700 rounded-xl">
              <Dice1 className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Click the button above to roll for LUCK</p>
            </div>
          )}
        </section>

        <section className="grid md:grid-cols-2 gap-6">
          {/* Core Attributes */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-5">
            <div>
              <h2 className="text-xl font-semibold mb-1">Core Attributes</h2>
              <p className="text-sm text-slate-400">STR + INT + POW ≤ 180</p>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "STR", value: str, setter: setStr, color: "red" },
                { label: "INT", value: intAttr, setter: setIntAttr, color: "blue" },
                { label: "POW", value: pow, setter: setPow, color: "purple" },
              ].map(({ label, value, setter, color }) => (
                <div key={label} className="space-y-2">
                  <label className="text-sm font-medium text-slate-300 block">{label}</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={value}
                    onChange={(e) => setter(parseInt(e.target.value) || 0)}
                    className="w-full rounded-lg bg-slate-800 border-2 border-slate-700 px-4 py-3 text-white text-center text-lg font-semibold focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
              ))}
            </div>
            <div
              className={`rounded-xl p-4 border-2 transition-all ${
                coreTotal > 180
                  ? "bg-red-900/30 border-red-500 shadow-lg shadow-red-500/20"
                  : coreTotal === 180
                  ? "bg-amber-900/30 border-amber-500 shadow-lg shadow-amber-500/20"
                  : "bg-emerald-900/30 border-emerald-500"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-300 font-medium">Total</span>
                <span className={`text-lg font-bold ${coreTotal > 180 ? "text-red-400" : coreTotal === 180 ? "text-amber-400" : "text-emerald-400"}`}>
                  {coreTotal}/180
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    coreTotal > 180 ? "bg-red-500" : coreTotal === 180 ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${Math.min((coreTotal / 180) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Skills */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-5">
            <div>
              <h2 className="text-xl font-semibold mb-1">Skills</h2>
              <p className="text-sm text-slate-400">Budget: {skillBudget} points (INT × 4)</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "SPOT", value: spot, setter: setSpot },
                { label: "LISTEN", value: listen, setter: setListen },
                { label: "STEALTH", value: stealth, setter: setStealth },
                { label: "CHARM", value: charm, setter: setCharm },
              ].map(({ label, value, setter }) => (
                <div key={label} className="space-y-2">
                  <label className="text-sm font-medium text-slate-300 block">{label}</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={value}
                    onChange={(e) => setter(parseInt(e.target.value) || 0)}
                    className="w-full rounded-lg bg-slate-800 border-2 border-slate-700 px-4 py-3 text-white text-center text-lg font-semibold focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
              ))}
            </div>
            <div
              className={`rounded-xl p-4 border-2 transition-all ${
                skillUsed > skillBudget
                  ? "bg-red-900/30 border-red-500 shadow-lg shadow-red-500/20"
                  : skillUsed === skillBudget
                  ? "bg-amber-900/30 border-amber-500 shadow-lg shadow-amber-500/20"
                  : "bg-emerald-900/30 border-emerald-500"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-300 font-medium">Points Used</span>
                <span className={`text-lg font-bold ${skillUsed > skillBudget ? "text-red-400" : skillUsed === skillBudget ? "text-amber-400" : "text-emerald-400"}`}>
                  {skillUsed}/{skillBudget}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mb-2">
                <div
                  className={`h-full transition-all duration-300 ${
                    skillUsed > skillBudget ? "bg-red-500" : skillUsed === skillBudget ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${Math.min((skillUsed / skillBudget) * 100, 100)}%` }}
                />
              </div>
              <p className="text-xs text-slate-400">
                Remaining: <span className="font-semibold text-slate-300">{Math.max(0, skillBudget - skillUsed)}</span>
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                <div className="text-xs text-slate-400 mb-1">SAN (Sanity)</div>
                <div className="text-xl font-bold text-emerald-300">{san}</div>
                <div className="text-xs text-slate-500 mt-1">= POW</div>
              </div>
              <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                <div className="text-xs text-slate-400 mb-1">LUCK</div>
                <div className="text-xl font-bold text-indigo-300">{bestLuck}</div>
                <div className="text-xs text-slate-500 mt-1">Rolled above</div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-xl font-semibold">Background</h2>
          <input
            placeholder="Character Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
          />
          <textarea
            placeholder="Enter your character background story..."
            rows={5}
            value={backgroundStory}
            onChange={(e) => setBackgroundStory(e.target.value)}
            className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
          />
        </section>

        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-xl font-semibold"
          >
            <Save className="w-4 h-4" />
            Save & Go to KP Chat
          </button>
        </div>
        </div>
      </section>
    </div>
  );
}

