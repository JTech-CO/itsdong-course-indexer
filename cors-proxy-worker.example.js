/*
 * itsdong-course-indexer — CORS 프록시 (Cloudflare Worker 예제)
 * ---------------------------------------------------------------
 * docs/index.html 의 "라이브 강좌 목록"은 브라우저에서 itsdong.com 을 직접 호출하는데,
 * itsdong.com 은 CORS 를 허용하지 않습니다. 이 워커가 itsdong.com 요청만 중계하며
 * 응답에 CORS 헤더를 붙여 줍니다. (강좌 데이터를 저장하지 않고 그대로 통과시킬 뿐입니다.)
 *
 * 배포 방법 (무료):
 *   1) https://dash.cloudflare.com → Workers & Pages → Create Worker
 *   2) 아래 코드를 붙여넣고 Deploy
 *   3) 발급된 주소(예: https://itsdong-proxy.<계정>.workers.dev)를
 *      웹페이지의 [⚙ 연결 설정]에 다음 형식으로 입력:
 *         https://itsdong-proxy.<계정>.workers.dev/?url=
 *
 * 오남용 방지를 위해 itsdong.com 도메인으로만 중계하도록 제한했습니다.
 */
export default {
  async fetch(request) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const target = new URL(request.url).searchParams.get("url");
    if (!target) return new Response("missing ?url=", { status: 400, headers: cors });

    let t;
    try { t = new URL(target); } catch { return new Response("bad url", { status: 400, headers: cors }); }
    if (t.hostname !== "www.itsdong.com" && t.hostname !== "itsdong.com")
      return new Response("forbidden host", { status: 403, headers: cors });

    const upstream = await fetch(t.toString(), {
      headers: { "User-Agent": "itsdong-course-indexer-proxy (open-source)" },
    });
    return new Response(await upstream.arrayBuffer(), {
      status: upstream.status,
      headers: {
        ...cors,
        "Content-Type": upstream.headers.get("Content-Type") || "text/html; charset=utf-8",
        "Cache-Control": "public, max-age=600",
      },
    });
  },
};
