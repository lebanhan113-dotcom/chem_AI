# Kết quả kiểm thử tính năng tài khoản giáo viên

- `node tests/test_auth_api.cjs`: đạt, REST đăng ký, email redirect, recovery, login, trạng thái pending, logout.
- `python tests/test_teacher_accounts.py`: đạt, giao diện đăng ký, quên mật khẩu, pending, teacher, admin mời giáo viên (Supabase được mô phỏng).
- `node tests/test_scoring.mjs`: đạt, chấm MCQ, đúng/sai, trả lời ngắn và tự luận chờ chấm.
- Phần SQL và API mới đã kiểm tra logic và guard phân quyền tĩnh; CHƯA kiểm thử thực thi PostgreSQL/Supabase LIVE hoặc email xác nhận thực tế.
- Chưa deploy vào tài khoản Vercel/Supabase thực tế của giáo viên.
