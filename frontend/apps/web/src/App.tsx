import { useState } from "react";
import { Button } from "@workspace/ui/components/button";
import { Input } from "./components/ui/input";


type ShortenResponse = {
  remark: string;
  short_url: string;
};

export function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ShortenResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function shortenURL() {
    try {
      setLoading(true);

      const response = await fetch(
        "https://url-shortner-hizq.vercel.app/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            longURL: url,
          }),
        }
      );
      if (!response.ok) {
        throw new Error("Failed to shorten URL");
      }

      const data: ShortenResponse = await response.json();

      setResult(data);
    } catch (error) {
      console.error(error);

      setResult({
        remark: "Something went wrong.",
        short_url: "",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-svh items-center justify-center p-6">
      <div className="w-full max-w-md space-y-6">

        <div>
          <h1 className="text-2xl font-bold">
            URL Shortener
          </h1>
        </div>

        <div className="flex gap-2">
  <Input
    value={url}
    onChange={(e) => setUrl(e.target.value)}
    type="url"
    placeholder="Enter your URL"
    className="h-12 flex-1"
  />

  <Button
    onClick={shortenURL}
    disabled={loading || !url}
    className="h-12 px-4"
  >
    {loading ? "Shortening..." : "Shorten"}
  </Button>
</div>

        {result && (
          <div className="rounded-lg border p-4 space-y-3">

            <p className="font-medium">
              {result.remark}
            </p>

            {result.short_url && (
              <a
                href={result.short_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 underline break-all"
              >
                {result.short_url}
              </a>
            )}

          </div>
        )}

      </div>
    </div>
  );
}