# EduPlan AI 7.7 - Student-friendly interface and grading

## What changed
- A simple six-item main navigation: Home, Select lesson, Practice, Test, Results, Learning resources.
- Home screen lets students select grade, chapter and lesson and start right away.
- Practice and Test have one-click 5, 10 or 15-question starters and collapsed advanced filters.
- All prior learning resources, error notes, mind maps, question bank, study sheets and DOCX downloads remain in the Resources hub.
- A Vercel API grades only previously reviewed answer keys, after student submission.

## Deploy full grading on Vercel
1. Create a PRIVATE GitHub repository; this private package contains the reviewed answer keys in api/grade.js.
2. Upload all files, retaining index.html, api/grade.js, js, css, data, assets and references.
3. Import the repository into Vercel, Framework Preset = Other, root = repository root.
4. Deploy and test the homepage, select a grade/chapter with reviewed questions, select Test and answer questions.
5. Click Complete / Submit. The app POSTs answers to /api/grade and displays checked correct answers and explanations.
6. If the API is offline, the attempt remains saved locally, and the app does NOT invent correct answers. Use Retry after the server is online.

## Deploy on GitHub Pages
Use the separate PUBLIC zip. It contains no answer keys and no grade API. Submit saves the answers, but grades/reviewed keys cannot be returned securely.

## Safety and limits
- 1958 total source questions; 379 previously flagged reviewed; 2 of those have unresolved tables and are excluded. 377 answer keys are available for post-submission review in the Vercel-only package.
- The review flags came from older datasets; this upgrade did not independently re-solve all 377 questions.
- The API has no student authentication, anti-cheat controls or one-time examination tokens. It is ONLY for formative self-practice, not official school examinations.
- Local results stay on each device. No centralized class reports are created by this static frontend.
- GitHub public repos expose source code including any keys inside. The Vercel grading package requires a PRIVATE repository.
- Neither package requires GEMINI_API_KEY or any API key entered by students.
