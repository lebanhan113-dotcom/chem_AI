# EduPlan AI 7.2 - release acceptance notes

## Verified in the current runtime

1. The original public bank files remain byte-for-byte equal to release 7.1: 809 questions in grade 10, 473 in grade 11 and 676 in grade 12; 1,958 unique IDs in total.
2. No `answer`, `correct`, `proposed_answer`, `explanation`, `review_status`, `answer_key` field occurs on any published question object.
3. `node --check` passes for `js/app.js` and `js/docx-export.js`.
4. Headless Chromium injected-script testing loads 1,958 questions, shows 13 navigation entries, filters grade 10 to chapter 1 / lesson 1, creates a five-question interactive session with no duplicate ID, records an answer, auto-advances to question 2, and maintains progress in localStorage.
5. The same browser testing generated actual Word files for an interactive practice, a worksheet and a history report, opened using python-docx; ZIP integrity checks pass and LibreOffice successfully rendered Word output.
6. A separate Word test embedded an original question PNG, confirmed a valid image relationship and a Word inline image, and rendered in LibreOffice.
7. The question browser displays a page of 12 original questions, and clicking a question starts a one-question interactive session.
8. Test/exam creation stores a session, and the Results page displays its history. At a 390-pixel viewport, there was no horizontal overflow or JavaScript exception in the tested flow.

## Not verified / not implemented

- Publication to an actual GitHub Pages / Vercel URL under the user's account, or end-to-end external hosting/network conditions.
- Secure online examination grading, account login, teacher approval console, centralized progress or school-wide usage analytics. These require private backend infrastructure; the public bundle intentionally excludes answer keys.
- Exact round-trip of all historic Word MathType equations, complex tables and OLE diagrams.
- A full user acceptance test of every possible combination of the 1,958 source questions, all 78 lessons, and every browser.

The buttons labeled 'I understood' and 'Need review' are self-evaluations, not correctness marks.
