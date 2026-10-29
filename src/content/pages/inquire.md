---
url: /inquire/
template: page
title: Check Dates and Inquire
nav_title: Check dates
eyebrow: Live availability
kicker: Inquire
seo_title: "Availability and Direct Booking | Yosemite Gateway Chalet, June Lake"
description: "See which nights are open at the Yosemite Gateway Chalet in June Lake, pick your dates, and inquire directly. Whole-home rental for up to 8 guests near Yosemite."
topic: book Yosemite Gateway Chalet
hero: eastern-sierra-sunset-panorama
hero_alt: "The sun going down over the Eastern Sierra and the Mono Basin"
lead: See which nights are open, choose your dates, and send them straight to us. We reply within a day.
hide_cta: true
updated: 2026-10-27
---
<section class="avail" id="availability" aria-labelledby="avail-h">
  <div class="avail-head">
    <h2 id="avail-h">Find your dates</h2>
    <p class="avail-help">Tap an arrival day, then a departure day. Booked nights are shaded.</p>
  </div>
  <div class="cal" data-cal>
    <div class="cal-nav">
      <button type="button" class="cal-arrow" data-cal-prev aria-label="Previous month"><span aria-hidden="true">&#8592;</span></button>
      <button type="button" class="cal-arrow" data-cal-next aria-label="Next month"><span aria-hidden="true">&#8594;</span></button>
    </div>
    <div class="cal-months" data-cal-months aria-live="polite"></div>
  </div>
  <p class="cal-legend" aria-hidden="true"><span><i class="lg-open"></i>Open</span><span><i class="lg-booked"></i>Booked</span><span><i class="lg-stay"></i>Your stay</span></p>
  <div class="cal-bar">
    <div class="cal-summary" data-cal-summary><span class="cs-label">Your stay</span><span class="cs-value">Choose an arrival day</span></div>
    <div class="cal-actions">
      <button type="button" class="cal-clear" data-cal-clear hidden>Clear</button>
      <button type="button" class="btn btn-solid" data-cal-go disabled>Request these dates</button>
    </div>
  </div>
  <p class="cal-status" data-cal-status>Loading live availability&hellip;</p>
</section>

<h2 id="inquiry-form">Send your inquiry</h2>

<form class="inquiry" name="inquiry" method="POST" action="/thank-you/" data-netlify="true" netlify-honeypot="company" novalidate>
<input type="hidden" name="form-name" value="inquiry">
<p class="hp" aria-hidden="true"><label for="company">Leave this field empty</label><input id="company" name="company" tabindex="-1" autocomplete="off"></p>
<div><label for="first">First name</label><input id="first" name="first_name" autocomplete="given-name" required></div>
<div><label for="last">Last name</label><input id="last" name="last_name" autocomplete="family-name" required></div>
<div><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div>
<div><label for="phone">Phone <span class="muted">(optional)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>
<div><label for="arrival">Arrival</label><input id="arrival" name="arrival" type="date" required></div>
<div><label for="departure">Departure</label><input id="departure" name="departure" type="date" required><p class="err" id="date-error" hidden>Departure needs to be after arrival.</p></div>
<div><label for="guests">Guests</label><select id="guests" name="guests" required><option value="">Select</option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option></select><p class="hint">The chalet sleeps a maximum of eight, including infants.</p></div>
<div><label for="source">How did you hear about us? <span class="muted">(optional)</span></label><select id="source" name="heard_about"><option value="">Select</option><option>Search engine</option><option>AI assistant</option><option>VRBO</option><option>Airbnb</option><option>Returning guest</option><option>Friend or family</option><option>Other</option></select></div>
<div class="full"><label for="message">Message</label><textarea id="message" name="message" required placeholder="Who is coming, what you would like to do, any questions."></textarea></div>
<div class="full" data-netlify-recaptcha="true"></div>
<div class="full"><button class="btn btn-solid" type="submit">Send inquiry</button></div>
</form>

{% if CHAT_ON %}
Got a question before you send it? <button type="button" class="link-btn" data-chat-open>Ask the chat</button>. It knows the house and the Loop, and it can check your dates. You can also book instantly on [VRBO](https://www.vrbo.com/452799) or [Airbnb](https://www.airbnb.com/h/yosemitechalet).
{% else %}
You can also book instantly on [VRBO](https://www.vrbo.com/452799) or [Airbnb](https://www.airbnb.com/h/yosemitechalet).
{% endif %}
