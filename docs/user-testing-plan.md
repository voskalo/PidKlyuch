# PidKlyuch — User Testing Plan, Feedback Form & Master Tracker

> **Owner:** Anton Vertyporokh (`docs/`)  
> **Participants:** All team members (Liubomyr, Anna, Anton — minimum **5 external testers each**, **15+ total**)  
> **Live Testing Window:** Wednesday, 18 November 2026 (morning/afternoon testing → afternoon fixes → Thursday demo & report PDF)

---

## 1. Objectives & Grading Alignment

To satisfy the course rubric and product validation goals:
1. **External real users only (no close friends):** Recruit people who actually order parcels from Amazon/eBay/AliExpress or plan to import a car into Ukraine.
2. **Feedback loop (4 pts):** Record who tried the live HTTPS prototype, how many completed the tasks, exact quotes, bugs/confusion observed, and **concrete UX/code fixes shipped on Wednesday afternoon**.
3. **Donation bonus:** Ask testers whether they are willing to make a small voluntary donation to a Ukrainian volunteer cause via the in-app donation button and collect **screenshot proof** for `docs/report.pdf`.

---

## 2. Moderator Testing Script (10-Minute Session)

Conduct sessions in person, over Telegram/Google Meet screen share, or asynchronously via link + Google Form. Ask testers to **think aloud** and test on their **phone first** (primary traffic channel) or desktop.

### 2.1 Introduction (1 minute — Ukrainian script)
> «Привіт! Дякую, що погодився(лась) протестувати **PidKlyuch («Під ключ»)** — наш калькулятор повної вартості розмитнення посилок та авто в Україні.  
> Ми тестуємо **сервіс, а не тебе** — якщо щось незрозуміло або кнопка не там, це наша помилка в інтерфейсі, і нам дуже важливо про це почути. Коментуй вголос усе, що бачиш або шукаєш на екрані. Зараз я дам тобі два типові життєві завдання.»

### 2.2 Task 1 — Parcel Above €150 & July 2027 Comparison (4 minutes)
**Prompt to user:**
> «Уяви, що ти хочеш замовити навушники з Amazon за **$220** із доставкою **$18**.  
> 1. Зареєструйся (або увійди) на сайті за посиланням.  
> 2. Порахуй, скільки реально коштуватимуть ці навушники з урахуванням мита, ПДВ і доставки в євро та гривнях.  
> 3. Поясни своїми словами за формулою на екрані, чому сума податку саме така.  
> 4. Перевір, як зміниться оподаткування (зокрема для посилок до €150) після правил **липня 2027 року**.»

**What the moderator observes (do not help unless stuck >60s):**
- Did the user find sign-up quickly, and did JWT auth persist cleanly?
- Did they enter price and shipping separately and select `USD` without confusion?
- Did they understand that only the excess above €150 is taxed today (10% duty + 20% VAT)?
- Did they notice the **"Сьогодні vs Липень 2027"** comparison and understand the €150 VAT change?

### 2.3 Task 2 — Used Car Import, History & Volunteer Donation (5 minutes)
**Prompt to user:**
> «Тепер уяви, що ти розглядаєш пригон авто з Німеччини: **2018 рік, дизель 2.0 л (`2000 см³`), ціна €10,000 + доставка до кордону €800** (або електромобіль за **€12,000** із батареєю **60 кВт·год**).  
> 1. Порахуй суму мита, акцизу, ПДВ та підсумкову ціну.  
> 2. Перейди в **Історію розрахунків** і знайди свої два збережені розрахунки.  
> 3. Натисни на кнопку **волонтерського донату** на сторінці: наскільки вона доречна та зрозуміла? Якщо калькулятор був корисним, чи готовий(а) ти закинути символічний донат (наприклад, 20–50 грн) і надіслати скріншот для підтвердження у нашому звіті?»

**What the moderator observes:**
- Was the EU origin (`EUR.1`) toggle understood (bought in EU ≠ EU origin)?
- Were users surprised by 20% VAT on electric vehicles in 2026, and did the UI notes explain why?
- Were both parcel and car entries visible in `/history` and easy to read on mobile?
- Any hesitation or broken UX on the donation link/button?

---

## 3. Google Form Questions (Copy-Paste Ready)

Create the team Google Form titled: **`PidKlyuch («Під ключ») — Відгук тестувальника`**

1. **Ваш нікнейм / ім'я або код тестувальника (`T-01`..`T-15`) та звідки ви перейшли (Telegram-чат шопінгу, авточат, студентський чат тощо)**  
   *Type:* Short answer (Required)
2. **Ваш досвід покупок / імпорту з-за кордону за останній рік:**  
   *Type:* Checkboxes / Multiple choice (Required)  
   - Замовляю посилки до €150 (AliExpress, Amazon, iHerb тощо)  
   - Замовляю посилки дорожче €150  
   - Приганяв(ла) або планую пригнати авто з-за кордону  
   - Поки не замовляв(ла), але цікавлюся  
3. **Чи вдалося вам без підказок зареєструватися, порахувати посилку й авто та знайти їх в історії?**  
   *Type:* Multiple choice (Required)  
   - Так, усе інтуїтивно  
   - Частково (потрібна була підказка або довелося пошукати)  
   - Ні, виникли помилки / не розібрався(лась)  
4. **Наскільки зрозумілою була деталізація мита, акцизу, ПДВ, формул і порівняння «Сьогодні vs Липень 2027»?**  
   *Type:* Linear scale `1` (Зовсім незрозуміло) — `5` (Дуже зрозуміло) (Required)
5. **Що саме викликало сумнів, дратувало або зламалося під час тестування?** *(Будь-які деталі допоможуть нам виправити інтерфейс до релізу!)*  
   *Type:* Paragraph (Required)
6. **Чи готові ви підтримати волонтерський збір (кнопку донату) за користування таким калькулятором?**  
   *Type:* Multiple choice (Required)  
   - Так, вже задонатив(ла) (надішлю/прикріплю скріншот)  
   - Готовий(а) задонатити 20–100 грн при реальному замовленні  
   - Поки ні  
7. **Коротка цитата: яке одне враження у вас залишилося від PidKlyuch?**  
   *Type:* Paragraph (Required)
8. **Скріншот підтвердження донату (необов'язково, для бонусного критерію звіту — можна також скинути в Telegram модератору):**  
   *Type:* File upload / Short answer (Optional)

---

## 4. Master Tester Tracking Table (15+ External Testers)

Record every completed session below on Wednesday, 18 November 2026 so Anton can compile `docs/report.pdf` cleanly.

| Tester ID | Recruited By | Channel / Community | User Profile | Scenario Tested | Completed? | Key Quote (Verbatim) | Bug / UX Issue Found | Action Taken / Fix | Donation Proof (Screenshot) |
|---|---|---|---|---|---|---|---|---|---|
| `T-01` | Anton | | | | | | | | |
| `T-02` | Anton | | | | | | | | |
| `T-03` | Anton | | | | | | | | |
| `T-04` | Anton | | | | | | | | |
| `T-05` | Anton | | | | | | | | |
| `T-06` | Liubomyr | | | | | | | | |
| `T-07` | Liubomyr | | | | | | | | |
| `T-08` | Liubomyr | | | | | | | | |
| `T-09` | Liubomyr | | | | | | | | |
| `T-10` | Liubomyr | | | | | | | | |
| `T-11` | Anna | | | | | | | | |
| `T-12` | Anna | | | | | | | | |
| `T-13` | Anna | | | | | | | | |
| `T-14` | Anna | | | | | | | | |
| `T-15` | Anna | | | | | | | | |

### Session Rollup Metrics (Fill In Wednesday Evening)
- **Total unique external testers:** `0 / 15+`
- **Backend `/api/stats` snapshot:** `users = __`, `calculations = __`, `returning_users = __`
- **Task completion rate (no help / partial):** `__%`
- **Average clarity score (Q4):** `__ / 5.0`
- **Top UX / bug fixes shipped from feedback:** *(list PR/commit links)*
- **Donations collected (count + total UAH + screenshots archived in `docs/evidence/`):** `0`
