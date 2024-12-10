export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const searchTerm = searchParams.get("searchTerm");
  const baseUrl = process.env.NEXT_PUBLIC_API_ENDPOINT;

  if (!baseUrl) {
    return new Response(
      JSON.stringify({ error: "API endpoint not configured" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  const apiUrl = `${baseUrl}/search/${encodeURIComponent(searchTerm)}`;

  try {
    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data from API: ${response.statusText}`);
    }

    const data = await response.json();

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in proxy:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
