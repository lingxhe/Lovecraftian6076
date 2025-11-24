"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Dice1, Save } from "lucide-react";
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
  const [selectedAvatar, setSelectedAvatar] = useState(character?.avatar || "🧑‍🔬");
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
    setLuckRolls((prev) => [...prev, result]);
    setRollCount((prev) => prev + 1);
    if (result > bestLuck) {
      setBestLuck(result);
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
      avatar: selectedAvatar,
      background_story: backgroundStory.trim(),
    };

    setCharacter(newCharacter);
    router.push("/chat");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white overflow-x-hidden">
      <section className="min-h-screen py-20">
        <div className="max-w-6xl mx-auto px-6 space-y-8">
          <header className="text-center space-y-4">
            <p className="text-sm uppercase tracking-wider text-slate-400">Call of Cthulhu Solo</p>
            <h1 className="text-4xl font-bold">Create Character</h1>
            <p className="text-slate-300 mt-3">
              Set up your CoC investigator. All information is saved locally in your browser.
            </p>
          </header>

        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Image Selection</h2>
          <div className="grid grid-cols-6 gap-4">
            {AVATAR_OPTIONS.map((emoji) => (
              <button
                key={emoji}
                onClick={() => setSelectedAvatar(emoji)}
                className={`p-4 rounded-xl border transition-all ${
                  selectedAvatar === emoji
                    ? "border-indigo-400 bg-indigo-500/20 scale-105"
                    : "border-slate-700 hover:border-slate-500"
                }`}
              >
                <div className="text-5xl">{emoji}</div>
                <p className="mt-2 text-xs text-slate-400">{selectedAvatar === emoji ? "Selected" : "Select"}</p>
              </button>
            ))}
          </div>
        </section>

        <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">LUCK</h2>
            <button
              onClick={rollLuck}
              disabled={rollCount >= 3}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700"
            >
              <Dice1 className="w-4 h-4" />
              Roll LUCK ({3 - rollCount} left)
            </button>
          </div>
          <p className="text-slate-300">Roll 3d6×5 to generate LUCK (can roll 3 times, keep the best result).</p>
          <div className="space-y-1 text-slate-200">
            {luckRolls.map((value, idx) => (
              <p key={idx}>
                Roll {idx + 1}: <span className="font-semibold">{value}</span>
              </p>
            ))}
            <p className="text-green-300 font-semibold mt-2">Best Luck: {bestLuck}</p>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
            <h2 className="text-xl font-semibold">Core Attributes</h2>
            <p className="text-slate-400">Total of STR + INT + POW must not exceed 180</p>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "STR", value: str, setter: setStr },
                { label: "INT", value: intAttr, setter: setIntAttr },
                { label: "POW", value: pow, setter: setPow },
              ].map(({ label, value, setter }) => (
                <div key={label}>
                  <label className="text-sm text-slate-400">{label}</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={value}
                    onChange={(e) => setter(parseInt(e.target.value) || 0)}
                    className="w-full mt-1 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
                  />
                </div>
              ))}
            </div>
            <div
              className={`mt-2 rounded-lg px-4 py-3 ${
                coreTotal > 180 ? "bg-red-900/40 border border-red-500" : "bg-emerald-900/30 border border-emerald-500"
              }`}
            >
              Core attributes total: {coreTotal}/180
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
            <h2 className="text-xl font-semibold">Skills</h2>
            <p className="text-slate-400">Skill points budget (INT × 4): {skillBudget} points (LUCK not included)</p>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "SPOT", value: spot, setter: setSpot },
                { label: "LISTEN", value: listen, setter: setListen },
                { label: "STEALTH", value: stealth, setter: setStealth },
                { label: "CHARM", value: charm, setter: setCharm },
              ].map(({ label, value, setter }) => (
                <div key={label}>
                  <label className="text-sm text-slate-400">{label}</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={value}
                    onChange={(e) => setter(parseInt(e.target.value) || 0)}
                    className="w-full mt-1 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
                  />
                </div>
              ))}
            </div>
            <div
              className={`mt-2 rounded-lg px-4 py-3 ${
                skillUsed > skillBudget
                  ? "bg-red-900/40 border border-red-500"
                  : "bg-emerald-900/30 border border-emerald-500"
              }`}
            >
              Skill points used: {skillUsed}/{skillBudget} (remaining: {skillBudget - skillUsed})
              <p className="text-sm text-slate-400 mt-1">
                SPOT({spot}) + LISTEN({listen}) + STEALTH({stealth}) + CHARM({charm})
              </p>
            </div>
            <div className="bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2">
              SAN (Sanity): <span className="font-semibold text-emerald-300">{san}</span> (equals POW)
              <br />
              LUCK: <span className="font-semibold text-indigo-300">{bestLuck}</span> (rolled above)
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

