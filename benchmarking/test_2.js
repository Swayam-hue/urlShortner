import http from "k6/http";

export default function () {
  const res = http.get(
    "https://urlshortner.fastapicloud.dev/gc",
    {
      redirects: 0,
    }
  );
  console.log(res.status);
}