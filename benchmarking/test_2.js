import http from "k6/http";

export const options = {
  vus: 100,
  duration: "1m",
};

export default function () {
  http.get(
    "https://urlshortner.fastapicloud.dev/gc",
    {
      redirects: 0,
    }
  );
}