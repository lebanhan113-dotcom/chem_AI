-- Thiết lập một lần trong Supabase SQL Editor SAU KHI tạo và xác minh email.
-- Cố ý KHÔNG đặt hay lưu mật khẩu trong SQL.
DO $$
DECLARE v_id uuid;
BEGIN
  SELECT id INTO v_id FROM auth.users
  WHERE lower(btrim(email)) = 'lebanhan113@gmail.com'
    AND email_confirmed_at IS NOT NULL
  LIMIT 1;
  IF v_id IS NULL THEN
    RAISE EXCEPTION 'Chưa tìm thấy tài khoản email đã xác minh. Tạo tài khoản trong Authentication > Users trước.';
  END IF;
  INSERT INTO public.app_profiles(id,role) VALUES(v_id,'admin')
  ON CONFLICT(id) DO UPDATE SET role = 'admin';
END $$;

-- Đối chiếu kết quả (chỉ chạy trong SQL Editor do chủ dự án quản lý):
SELECT u.email, p.role FROM auth.users AS u JOIN public.app_profiles p ON p.id=u.id
WHERE lower(btrim(u.email)) = 'lebanhan113@gmail.com';
