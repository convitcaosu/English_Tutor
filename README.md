# English AI Tutor — bản mẫu v1

## Chạy trên Windows
1. Giải nén ra folder mới.
2. Bấm đúp `CHAY_APP.bat` (lần đầu sẽ cài thư viện).
3. Chọn trình độ + chủ đề, tick "Dùng mic" nếu muốn nói, bấm **Bắt đầu phiên**.
4. AI nói trước, bạn nói lại (hoặc gõ tay vào ô dưới nếu mic lỗi), AI nói tiếp.
5. Bấm **Dừng** là mic ngừng nghe ngay. Bấm **Tổng kết buổi học** để xem lại số lượt nói.

Muốn có exe thật: chạy `build_exe.bat`, rồi chạy `dist\EnglishTutor\EnglishTutor.exe`.

## Key API (tùy chọn, không bắt buộc cho bản mẫu)
Không có key thì app chạy chế độ demo: vẫn mở chuyện, hỏi tiếp, sửa nhẹ theo mẫu có sẵn.
Có key Gemini thì AI trả lời tự do hơn: tạo file `tutor/settings.json` với nội dung
`{"gemini_api_key": "KEY_CUA_BAN"}` trên máy Windows của bạn, KHÔNG gửi key qua chat,
KHÔNG đưa file này lên GitHub. File settings.json đã được gitignore.

## Giới hạn bản mẫu
- Chưa có khay hệ thống (system tray) và hẹn giờ nhắc học — đó là bước tiếp theo, không phải bản mẫu này.
- Chấm phát âm chỉ tương đối, độ trễ 1-3 giây tùy mạng/API.
- Mic chỉ nghe trong phiên đã bấm Bắt đầu, không nghe lén 24/7.
- Chưa test giọng nói thật trên Windows trên máy Linux này — cần bạn chạy CHAY_APP.bat và thử nói thật.

## Bản 3D v2 — nhân vật 3D thật (Ursina)
- Chạy `CHAY_3D.bat` (không phải CHAY_APP.bat) để mở cửa sổ 3D riêng.
- Nhân vật dựng bằng hình học 3D thật (đầu, thân, tay, mắt, miệng), có ánh sáng và camera xoay chậm để thấy chiều sâu.
- Miệng mở/đóng theo nhịp lúc AI nói, mắt chớp định kỳ, đầu nghiêng khi AI đang nghĩ.
- Giới hạn v2: miệng nhép theo nhịp, KHÔNG phải lip-sync theo từng âm tiết; nhân vật low-poly phong cách, KHÔNG phải người thật như Ready Player Me.

## Bản 3D v3 — 1 click, mic thật, AI có logic
- Gói thành application: chạy `build_exe_3d.bat` 1 lần trên Windows, sau đó chỉ cần nhấp đúp `dist\EnglishTutor3D\EnglishTutor3D.exe` là mở luôn giao diện 3D, không cần Python, không cần CHAY bat nữa. CHAY_3D.bat cũng tự chạy exe nếu đã build rồi.
- Mic thật trong cửa sổ 3D: sau khi AI nói xong, app tự nghe mic, chữ mic nghe được hiện lên màn hình, rồi AI trả lời. Nút "Mic: Speak" để nói lại, nút "Mic ON/OFF" để tắt. Nếu mic lỗi (chưa cấp quyền, chưa cài PyAudio, không có mic) thì gõ tay vẫn học tiếp được, app không crash.
- Logic AI đã sửa (lỗi user báo): khi bạn nói "wtf u mean" / "what do you mean" / "huh" / "repeat", AI KHÔNG hỏi câu không liên quan nữa, mà nói lại câu vừa nói bằng từ đơn giản hơn và hỏi phần nào chưa rõ. Khi bạn trả lời, AI nhắc lại đúng cái bạn vừa nói rồi mới hỏi tiếp. Với key Gemini thì luật này cũng đã đưa vào prompt, nên AI thật càng ít hỏi lệch. Chế độ demo không key vẫn là script, không thông minh bằng LLM — muốn AI nói chuyện thật thì cần key Gemini.
- Giới hạn còn lại: exe Windows phải build trên Windows, máy Linux này không build được exe Windows; mic và cửa sổ 3D vẫn cần bạn chạy thử trên Windows và báo lại.

## Bản v4 — 1 file exe duy nhất (giống QuantResearchLab)
- Trước đây build dùng --onedir nên ra cả folder dist\EnglishTutor3D\ với nhiều file, nhìn rối và khó copy.
- Từ v4, build_exe_3d.bat dùng --onefile nên ra đúng 1 file: dist\EnglishTutor3D.exe. Copy 1 file đó ra Desktop là xong, nhấp đúp là chạy.
- Đánh đổi thật: file 1 file sẽ to hơn và lần đầu chạy chậm hơn vì nó tự giải nén ra folder temp; bản 3D dùng Ursina nên sẽ KHÔNG nhẹ 28MB như QuantResearchLab (app đó nhẹ hơn nhiều), mà có thể 150-300MB, vì engine 3D + Python + thư viện giọng nói đều nặng. App không 3D (main.py) đóng 1 file sẽ nhẹ hơn nhiều, gần mức đó hơn.
- Sửa kèm: khi đóng 1 file, key trong settings.json phải để cạnh file exe (hoặc cạnh folder tutor), app đã sửa để tìm đúng chỗ đó, không tìm nhầm vào folder temp nữa.
- Nếu bản onefile bị lỗi với Ursina, chạy build_exe_3d_onedir.bat để về bản folder cũ ổn định hơn.
