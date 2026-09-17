const CONTACT_TO = "pamir@pamilanga.com";
const CONTACT_FROM = "pamir@pamilanga.com";

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
});

const clean = (value, max = 2000) => String(value || "").trim().slice(0, max);
const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

const CONTACT_SECTION = `
<style>
#contact{background:#0b1115;border-top:1px solid rgba(255,255,255,.12);padding:96px 0}.pamir-contact{width:min(1120px,calc(100% - 72px));margin:auto;display:grid;grid-template-columns:.85fr 1.15fr;gap:72px;align-items:start}.pamir-contact .eyebrow{margin:0 0 18px;color:#54db86;font-size:11px;letter-spacing:.16em;text-transform:uppercase}.pamir-contact h2{font-size:clamp(34px,4vw,58px);line-height:1.02;margin:0 0 24px}.pamir-contact-copy{color:#9ca7ad;line-height:1.7;max-width:520px}.pamir-contact-mail{display:inline-block;margin-top:24px;color:#fff;border-bottom:1px solid rgba(255,255,255,.45);padding-bottom:5px}.pamir-form{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pamir-field{display:flex;flex-direction:column;gap:8px}.pamir-field.full{grid-column:1/-1}.pamir-field label{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:#9ca7ad}.pamir-field input,.pamir-field select,.pamir-field textarea{width:100%;background:#11191e;color:#f3f5f6;border:1px solid rgba(255,255,255,.16);padding:15px 16px;font:inherit;outline:none}.pamir-field input:focus,.pamir-field select:focus,.pamir-field textarea:focus{border-color:#54db86}.pamir-field textarea{min-height:150px;resize:vertical}.pamir-submit{grid-column:1/-1;display:flex;align-items:center;gap:18px}.pamir-submit button{min-height:48px;padding:0 24px;background:#f3f5f6;color:#070b0e;border:0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;cursor:pointer}.pamir-submit button:disabled{opacity:.55;cursor:wait}.pamir-status{font-size:12px;color:#9ca7ad}.pamir-status.ok{color:#54db86}.pamir-status.err{color:#ff8c8c}.pamir-hp{position:absolute!important;left:-9999px!important;width:1px!important;height:1px!important;overflow:hidden!important}@media(max-width:820px){#contact{padding:72px 0}.pamir-contact{width:min(100% - 36px,1120px);grid-template-columns:1fr;gap:40px}.pamir-form{grid-template-columns:1fr}.pamir-field.full,.pamir-submit{grid-column:1}.pamir-submit{align-items:flex-start;flex-direction:column}}
</style>
<section id="contact" aria-labelledby="contact-title">
  <div class="pamir-contact">
    <div>
      <p class="eyebrow">Contact / Pilot inquiry</p>
      <h2 id="contact-title">Bring us a real autonomy problem.</h2>
      <p class="pamir-contact-copy">For technical validation, pilot programmes, research collaboration and investor enquiries, send the PAMIR team a short brief. We review each enquiry directly.</p>
      <a class="pamir-contact-mail" href="mailto:pamir@pamilanga.com">pamir@pamilanga.com</a>
    </div>
    <form class="pamir-form" id="pamir-contact-form" novalidate>
      <div class="pamir-field"><label for="pc-name">Name</label><input id="pc-name" name="name" autocomplete="name" maxlength="120" required></div>
      <div class="pamir-field"><label for="pc-org">Organisation</label><input id="pc-org" name="organisation" autocomplete="organization" maxlength="160" required></div>
      <div class="pamir-field full"><label for="pc-email">Work email</label><input id="pc-email" name="email" type="email" autocomplete="email" maxlength="200" required></div>
      <div class="pamir-field full"><label for="pc-interest">Area of interest</label><select id="pc-interest" name="interest" required><option value="">Select</option><option>Technical validation</option><option>Pilot programme</option><option>Research collaboration</option><option>Investment</option><option>Other</option></select></div>
      <div class="pamir-field full"><label for="pc-message">Message</label><textarea id="pc-message" name="message" maxlength="4000" required placeholder="Tell us what you are validating, the system context, and what evidence you need."></textarea></div>
      <div class="pamir-hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
      <div class="pamir-submit"><button type="submit">Send inquiry →</button><span class="pamir-status" role="status" aria-live="polite"></span></div>
    </form>
  </div>
</section>
<script>
(()=>{const f=document.getElementById('pamir-contact-form');if(!f)return;const b=f.querySelector('button');const s=f.querySelector('.pamir-status');f.addEventListener('submit',async(e)=>{e.preventDefault();s.className='pamir-status';if(!f.reportValidity())return;b.disabled=true;s.textContent='Sending…';try{const payload=Object.fromEntries(new FormData(f).entries());const r=await fetch('/api/contact',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||'Unable to send your message.');f.reset();s.className='pamir-status ok';s.textContent='Message received. The PAMIR team will respond by email.'}catch(err){s.className='pamir-status err';s.textContent=err.message||'Unable to send your message.'}finally{b.disabled=false}})})();
</script>`;

class FooterInjector {
  element(element) {
    element.before(CONTACT_SECTION, { html: true });
  }
}

class ContactLinkHandler {
  element(element) {
    const href = element.getAttribute("href") || "";
    if (href.toLowerCase().startsWith("mailto:pamir@pamilanga.com")) {
      element.setAttribute("href", "#contact");
    }
  }
}

async function handleContact(request, env) {
  if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
  const type = request.headers.get("content-type") || "";
  if (!type.includes("application/json")) return json({ error: "Invalid request" }, 415);

  let body;
  try { body = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }

  const name = clean(body.name, 120);
  const organisation = clean(body.organisation, 160);
  const email = clean(body.email, 200).toLowerCase();
  const interest = clean(body.interest, 120);
  const message = clean(body.message, 4000);
  const honeypot = clean(body.website, 200);

  if (honeypot) return json({ ok: true });
  if (!name || !organisation || !validEmail(email) || !interest || message.length < 10) {
    return json({ error: "Please complete all required fields with a valid work email." }, 400);
  }
  if (!env.EMAIL || typeof env.EMAIL.send !== "function") {
    return json({ error: "Contact service is being configured. Please email pamir@pamilanga.com directly." }, 503);
  }

  const subject = `[PAMIR] ${interest} — ${organisation}`;
  const text = `PAMIR website inquiry\n\nName: ${name}\nOrganisation: ${organisation}\nWork email: ${email}\nArea of interest: ${interest}\n\nMessage:\n${message}\n`;
  const esc = (v) => v.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const html = `<h2>PAMIR website inquiry</h2><p><b>Name:</b> ${esc(name)}</p><p><b>Organisation:</b> ${esc(organisation)}</p><p><b>Work email:</b> ${esc(email)}</p><p><b>Area of interest:</b> ${esc(interest)}</p><hr><p style="white-space:pre-wrap">${esc(message)}</p>`;

  try {
    await env.EMAIL.send({ to: CONTACT_TO, from: CONTACT_FROM, replyTo: email, subject, text, html });
    return json({ ok: true });
  } catch (error) {
    console.error("PAMIR contact email failed", error);
    return json({ error: "Unable to send your message right now. Please email pamir@pamilanga.com directly." }, 502);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/contact") return handleContact(request, env);

    const response = await env.ASSETS.fetch(request);
    const type = response.headers.get("content-type") || "";
    if (!type.includes("text/html")) return response;

    return new HTMLRewriter()
      .on("footer", new FooterInjector())
      .on('a[href^="mailto:pamir@pamilanga.com"]', new ContactLinkHandler())
      .transform(response);
  },
};
