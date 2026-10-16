hero_ignus_attack

frames/        Mỗi frame một PNG, đúng kích thước gốc của frame (size). Phần ảnh có nội dung
               đã được đặt lại đúng chỗ (trim_offset), nên các frame chồng lên nhau là khớp.
manifest.json  Thông tin từng frame: size, trim_offset, content, atlas gốc và quad_in_atlas,
               alias_of (frame trùng ảnh với frame khác). "animations" giữ thứ tự frame và
               định nghĩa gốc trong game_animations; fps chung của game là 30.

Khi vẽ lại: giữ tên file và kích thước canvas của từng frame để công cụ đóng gói atlas
tính lại trim và vị trí. Frame có alias_of chỉ cần sửa một lần ở frame gốc.