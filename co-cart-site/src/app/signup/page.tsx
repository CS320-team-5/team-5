import { ArrowRight, MapPin } from "lucide-react";

export default function SignUpPage() {
  return (
    <main className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6">
        <h1 className="text-3xl font-bold">
          Co-Cart<span className="text-green-700">.</span>
        </h1>

        <button>Log In</button>
      </header>

      {/* Card */}
      <div className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-[580px] bg-white rounded-3xl p-10 shadow-sm">
          <h2 className="text-4xl font-bold text-center">
            Create Account
          </h2>

          <p className="text-center text-gray-500 mt-2">
            Pool delivery minimums with your building or neighbors.
          </p>

          <div className="grid grid-cols-2 gap-3 mt-8">
            <button className="bg-slate-100 rounded-xl py-4">
              Google
            </button>

            <button className="bg-slate-100 rounded-xl py-4">
              Apple
            </button>
          </div>

          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-sm text-gray-500">
              OR EMAIL
            </span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          <div className="space-y-4">
            <div>
              <label className="block mb-1 font-medium">
                Full Name
              </label>
              <input
                className="w-full border rounded-xl p-4"
                placeholder="e.g. Maya Lin"
              />
            </div>

            <div>
              <label className="block mb-1 font-medium">
                Email Address
              </label>
              <input
                className="w-full border rounded-xl p-4"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block mb-1 font-medium">
                Building Address / Zip
              </label>

              <div className="relative">
                <input
                  className="w-full border rounded-xl p-4"
                  placeholder="e.g. 75 Montague St or 11201"
                />

                <MapPin
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
              </div>
            </div>

            <div>
              <label className="block mb-1 font-medium">
                Password
              </label>
              <input
                className="w-full border rounded-xl p-4"
                placeholder="8+ characters"
              />
            </div>
          </div>

          <label className="flex items-center gap-3 mt-5">
            <input type="checkbox" />
            <span className="text-gray-600">
              Alert me when neighbors start an order
            </span>
          </label>

          <button className="w-full bg-green-800 text-white rounded-xl py-4 mt-6 flex items-center justify-center gap-2 text-lg font-semibold">
            Create Account
            <ArrowRight size={20} />
          </button>

          <p className="text-center mt-5 text-gray-500">
            Already have an account?
            <span className="text-green-700 ml-2 cursor-pointer">
              Log in
            </span>
          </p>
        </div>
      </div>

      <footer className="text-center py-6 text-gray-500">
        Co-Cart · Group order pooling
      </footer>
    </main>
  );
}