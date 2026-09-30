const ALLOWED_FIELDS = [
  "title","slug","department","advertisement_number","post_name","category","total_posts","location",
  "application_start","application_end","fee_last_date","correction_date","exam_date","admit_card_date","result_date",
  "general_fee","obc_ews_fee","sc_st_fee","female_fee","payment_method",
  "minimum_age","maximum_age","age_relaxation","vacancy_details","qualification","experience","other_conditions",
  "description","apply_url","notification_url","official_url","admit_card_url","result_url","answer_key_url",
  "seo_title","meta_description","keywords","status"
];

function env(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing environment variable: ${name}`);
  return value;
}

function isAdmin(req) {
  const auth = req.headers.authorization || "";
  return auth === `Bearer ${process.env.ADMIN_API_TOKEN || ""}`;
}

function cleanPayload(body = {}) {
  const out = {};
  for (const key of ALLOWED_FIELDS) {
    if (Object.prototype.hasOwnProperty.call(body, key)) out[key] = body[key];
  }
  return out;
}

async function supabase(path, options = {}) {
  const url = env("SUPABASE_URL").replace(/\/$/, "") + "/rest/v1/" + path;
  const key = env("SUPABASE_SERVICE_ROLE_KEY");
  const response = await fetch(url, {
    ...options,
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      Prefer: options.prefer || "return=representation",
      ...(options.headers || {})
    }
  });

  const text = await response.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }
  if (!response.ok) {
    const error = new Error(typeof data === "string" ? data : (data?.message || "Database request failed"));
    error.status = response.status;
    throw error;
  }
  return data;
}

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");

  try {
    if (req.method === "GET") {
      const { slug, admin, limit = "50" } = req.query || {};
      let query = "jobs?select=*&order=created_at.desc";

      if (slug) {
        query += `&slug=eq.${encodeURIComponent(slug)}`;
        if (!isAdmin(req)) query += "&status=eq.Published";
        query += "&limit=1";
      } else if (admin === "1") {
        if (!isAdmin(req)) return res.status(401).json({ error: "Unauthorized" });
        query += `&limit=${Math.min(Number(limit) || 50, 200)}`;
      } else {
        query += `&status=eq.Published&limit=${Math.min(Number(limit) || 50, 100)}`;
      }

      const data = await supabase(query, { method: "GET" });
      return res.status(200).json(slug ? (data?.[0] || null) : data);
    }

    if (!isAdmin(req)) return res.status(401).json({ error: "Unauthorized" });

    if (req.method === "POST") {
      const payload = cleanPayload(req.body);
      if (!payload.title || !payload.slug) {
        return res.status(400).json({ error: "title and slug are required" });
      }
      const data = await supabase("jobs", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      return res.status(201).json(data?.[0] || data);
    }

    if (req.method === "PUT") {
      const id = req.query?.id;
      if (!id) return res.status(400).json({ error: "id is required" });
      const payload = cleanPayload(req.body);
      const data = await supabase(`jobs?id=eq.${encodeURIComponent(id)}`, {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      return res.status(200).json(data?.[0] || data);
    }

    if (req.method === "DELETE") {
      const id = req.query?.id;
      if (!id) return res.status(400).json({ error: "id is required" });
      await supabase(`jobs?id=eq.${encodeURIComponent(id)}`, {
        method: "DELETE",
        prefer: "return=minimal"
      });
      return res.status(204).end();
    }

    res.setHeader("Allow", "GET,POST,PUT,DELETE");
    return res.status(405).json({ error: "Method not allowed" });
  } catch (error) {
    console.error(error);
    return res.status(error.status || 500).json({ error: error.message || "Server error" });
  }
};