-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 29, 2022 at 03:59 PM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 8.0.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `qlsv`
--

-- --------------------------------------------------------

--
-- Table structure for table `dang_ky_mon`
--

CREATE TABLE `dang_ky_mon` (
  `id_dang_ky` int(11) NOT NULL,
  `ma_sinh_vien` int(11) NOT NULL,
  `la_yeu_cau` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `diem`
--

CREATE TABLE `diem` (
  `id_diem` int(11) NOT NULL,
  `ma_sinh_vien` int(11) DEFAULT NULL,
  `ma_mon` varchar(15) DEFAULT NULL,
  `ma_hoc_ky` varchar(15) DEFAULT NULL,
  `he_so_1` float DEFAULT NULL,
  `he_so_2` float DEFAULT NULL,
  `he_so_3` float DEFAULT NULL,
  `diem_he_1` float DEFAULT NULL,
  `diem_he_2` float DEFAULT NULL,
  `diem_he_3` float DEFAULT NULL,
  `thang_10` float DEFAULT NULL,
  `thang_4` float DEFAULT NULL,
  `thang_chu` varchar(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Triggers `diem`
--
DELIMITER $$
CREATE TRIGGER `after_insert_diem` BEFORE INSERT ON `diem` FOR EACH ROW BEGIN
DECLARE diem10 double;
DECLARE diem4 double;
DECLARE diem_chu varchar(2);

IF NEW.diem_he_1 IS NOT NULL AND NEW.diem_he_2 IS NOT NULL AND NEW.diem_he_3 IS NOT NULL THEN
	SET diem10 = ROUND(NEW.he_so_1 * NEW.diem_he_1 + NEW.he_so_2 * NEW.diem_he_2 + NEW.he_so_3 * NEW.diem_he_3, 1);
    
    IF diem10  < 4.0 THEN
    	SET diem4 = 0;
        SET diem_chu = 'F';
    ELSEIF diem10 < 5 THEN
    	SET diem4 = 1;
        SET diem_chu = 'D';
    ELSEIF diem10 < 5.5 THEN
    	SET diem4 = 1.5;
        SET diem_chu = 'D+';
    ELSEIF diem10 < 6.5 THEN
    	SET diem4 = 2;
        SET diem_chu = 'C';
    ELSEIF diem10 < 7 THEN
    	SET diem4 = 2.5;
        SET diem_chu = 'C+';
    ELSEIF diem10 < 8 THEN
    	SET diem4 = 3;
        SET diem_chu = 'B';
    ELSEIF diem10 < 8.5 THEN
    	SET diem4 = 3.5;
        SET diem_chu = 'B+';
    ELSEIF diem10 < 9 THEN
    	SET diem4 = 3.7;
        SET diem_chu = 'A';
    ELSE
    	SET diem4 = 4;
        SET diem_chu = 'A+';
    END IF;
    
    SET NEW.thang_10 = diem10;
    SET NEW.thang_4 = diem4;
    SET NEW.thang_chu = diem_chu;
END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_update_diem` BEFORE UPDATE ON `diem` FOR EACH ROW BEGIN
DECLARE diem10 double;
DECLARE diem4 double;
DECLARE diem_chu varchar(2);

IF NEW.diem_he_1 IS NOT NULL AND NEW.diem_he_2 IS NOT NULL AND NEW.diem_he_3 IS NOT NULL THEN
	SET diem10 = ROUND(NEW.he_so_1 * NEW.diem_he_1 + NEW.he_so_2 * NEW.diem_he_2 + NEW.he_so_3 * NEW.diem_he_3, 1);
    
    IF diem10  < 4.0 THEN
    	SET diem4 = 0;
        SET diem_chu = 'F';
    ELSEIF diem10 < 5 THEN
    	SET diem4 = 1;
        SET diem_chu = 'D';
    ELSEIF diem10 < 5.5 THEN
    	SET diem4 = 1.5;
        SET diem_chu = 'D+';
    ELSEIF diem10 < 6.5 THEN
    	SET diem4 = 2;
        SET diem_chu = 'C';
    ELSEIF diem10 < 7 THEN
    	SET diem4 = 2.5;
        SET diem_chu = 'C+';
    ELSEIF diem10 < 8 THEN
    	SET diem4 = 3;
        SET diem_chu = 'B';
    ELSEIF diem10 < 8.5 THEN
    	SET diem4 = 3.5;
        SET diem_chu = 'B+';
    ELSEIF diem10 < 9 THEN
    	SET diem4 = 3.7;
        SET diem_chu = 'A';
    ELSE
    	SET diem4 = 4;
        SET diem_chu = 'A+';
    END IF;
    
    SET NEW.thang_10 = diem10;
    SET NEW.thang_4 = diem4;
    SET NEW.thang_chu = diem_chu;
END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `dot_dang_ky`
--

CREATE TABLE `dot_dang_ky` (
  `ma_dot` int(11) NOT NULL,
  `ma_hoc_ky` varchar(15) DEFAULT NULL,
  `ngay_bat_dau` datetime DEFAULT NULL,
  `ngay_ket_thuc` datetime DEFAULT NULL,
  `trang_thai` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dot_yeu_cau_dang_ky`
--

CREATE TABLE `dot_yeu_cau_dang_ky` (
  `ma_dot_yeu_cau` int(11) NOT NULL,
  `ma_hoc_ky` varchar(15) DEFAULT NULL,
  `ngay_bat_dau` datetime DEFAULT NULL,
  `ngay_ket_thuc` datetime DEFAULT NULL,
  `trang_thai` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `gia_dinh`
--

CREATE TABLE `gia_dinh` (
  `ma_sinh_vien` int(11) NOT NULL,
  `ten_cha` varchar(70) NOT NULL,
  `nam_sinh_cha` year(4) NOT NULL,
  `sdt_cha` varchar(11) NOT NULL,
  `nghe_cha` varchar(50) NOT NULL,
  `email_cha` varchar(40) NOT NULL,
  `dia_chi_cha` varchar(100) NOT NULL,
  `noi_cha` varchar(100) NOT NULL,
  `ten_me` varchar(70) NOT NULL,
  `nam_sinh_me` year(4) NOT NULL,
  `sdt_me` varchar(11) NOT NULL,
  `nghe_me` varchar(50) NOT NULL,
  `email_me` varchar(40) NOT NULL,
  `dia_chi_me` varchar(100) NOT NULL,
  `noi_me` varchar(100) NOT NULL,
  `ten_vo_chong` varchar(70) NOT NULL,
  `ngay_sinh_vo_chong` date NOT NULL,
  `nghe_vo_chong` varchar(50) NOT NULL,
  `dia_chi_vo_chong` varchar(100) NOT NULL,
  `thong_tin_anh_chi_em` varchar(255) NOT NULL,
  `thong_tin_cac_con` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `gia_dinh`
--

INSERT INTO `gia_dinh` (`ma_sinh_vien`, `ten_cha`, `nam_sinh_cha`, `sdt_cha`, `nghe_cha`, `email_cha`, `dia_chi_cha`, `noi_cha`, `ten_me`, `nam_sinh_me`, `sdt_me`, `nghe_me`, `email_me`, `dia_chi_me`, `noi_me`, `ten_vo_chong`, `ngay_sinh_vo_chong`, `nghe_vo_chong`, `dia_chi_vo_chong`, `thong_tin_anh_chi_em`, `thong_tin_cac_con`) VALUES
(20002055, '', 1978, '', '', '', '', '', '', 1972, '', '', '', '', '', '', '0000-00-00', '', '', '', ''),
(20002062, '', 0000, '', '', '', '', '', '', 0000, '', '', '', '', '', '', '0000-00-00', '', '', '', ''),
(20002076, '', 0000, '', '', '', '', '', '', 0000, '', '', '', '', '', '', '0000-00-00', '', '', '', ''),
(20002077, '', 0000, '', '', '', '', '', '', 0000, '', '', '', '', '', '', '0000-00-00', '', '', '', ''),
(20002080, '', 0000, '', '', '', '', '', '', 0000, '', '', '', '', '', '', '0000-00-00', '', '', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `hoc_ky`
--

CREATE TABLE `hoc_ky` (
  `ma_hoc_ky` varchar(15) NOT NULL,
  `ten_hoc_ky` varchar(50) DEFAULT NULL,
  `nam_hoc` year(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `hoc_ky`
--

INSERT INTO `hoc_ky` (`ma_hoc_ky`, `ten_hoc_ky`, `nam_hoc`) VALUES
('HK200', 'Học Kỳ 2 - 2020 - 2021', 2020),
('HK201', 'Học Kỳ 1 - 2021 - 2022', 2021),
('HK202', 'Học Kỳ 2 - 2021 - 2022', 2021);

-- --------------------------------------------------------

--
-- Table structure for table `image_data`
--

CREATE TABLE `image_data` (
  `id_image` varchar(50) NOT NULL,
  `path_to_image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `image_data`
--

INSERT INTO `image_data` (`id_image`, `path_to_image`) VALUES
('Image_Profile_20002076', 'web/img/Image_Profile_20002076.jpg'),
('none_image_profile', 'web/img/No_Image.png');

-- --------------------------------------------------------

--
-- Table structure for table `khoa`
--

CREATE TABLE `khoa` (
  `ma_khoa` varchar(20) NOT NULL,
  `ten_khoa` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `khoa`
--

INSERT INTO `khoa` (`ma_khoa`, `ten_khoa`) VALUES
('TCT', 'Toán - Cơ - Tin học'),
('VATLY', 'Vật Lý');

-- --------------------------------------------------------

--
-- Table structure for table `loai_he`
--

CREATE TABLE `loai_he` (
  `ma_he` varchar(5) NOT NULL,
  `ten_he` varchar(50) DEFAULT NULL,
  `hoc_phi_tin_chi` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `loai_he`
--

INSERT INTO `loai_he` (`ma_he`, `ten_he`, `hoc_phi_tin_chi`) VALUES
('CLC', 'Chất Lượng Cao', 990000),
('HC', 'Chuẩn', 330000);

-- --------------------------------------------------------

--
-- Table structure for table `lop`
--

CREATE TABLE `lop` (
  `ma_lop` varchar(30) NOT NULL,
  `ma_nganh` varchar(20) DEFAULT NULL,
  `nam` year(4) DEFAULT NULL,
  `ten_lop` varchar(100) DEFAULT NULL,
  `ma_nguoi_quan_ly` int(11) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `lop`
--

INSERT INTO `lop` (`ma_lop`, `ma_nganh`, `nam`, `ten_lop`, `ma_nguoi_quan_ly`, `is_delete`) VALUES
('KHDL2020', 'KHDL', 2020, 'K65A5', NULL, 0),
('KHDL2021', 'KHDL', 2021, 'K66A5', NULL, 0),
('KHDL2022', 'KHDL', 2022, 'K67A5', NULL, 0),
('KMHTTT2020', 'KHMTTT', 2020, 'K65A7', NULL, 0),
('TT2020', 'TT', 2020, 'K65A2', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `mon_hoc`
--

CREATE TABLE `mon_hoc` (
  `ma_mon` varchar(15) NOT NULL,
  `ten_mon` varchar(50) DEFAULT NULL,
  `so_tin_chi` int(11) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `mon_hoc`
--

INSERT INTO `mon_hoc` (`ma_mon`, `ten_mon`, `so_tin_chi`, `is_delete`) VALUES
('FLF1107', 'Tiếng Anh B1', 5, 0),
('GEO1050', 'Khoa học trái đất và sự sống', 3, 0),
('HIS1001', 'Lịch sử Đảng Cộng sản Việt Nam', 2, 0),
('HIS1056', 'Cơ sở văn hóa Việt Nam', 3, 0),
('INM1000', 'Tin học cơ sở', 2, 0),
('MAT1060', 'Nhập môn phân tích dữ liệu', 2, 0),
('MAT2034', 'Giải tích số', 3, 0),
('MAT2300', 'Đại số tuyến tính 1', 4, 0),
('MAT2301', 'Đại số tuyến tính 2', 4, 0),
('MAT2302', 'Giải tích 1', 5, 0),
('MAT2303', 'Giải tích 2', 5, 0),
('MAT2304', 'Giải tích 3', 4, 0),
('MAT2308', 'Xác suất 1', 3, 0),
('MAT2310', 'Hình học giải tích', 2, 0),
('MAT2311', 'Thống kê ứng dụng', 4, 0),
('MAT2314', 'Phương trình vi phân', 4, 0),
('MAT2315', 'Phương pháp nghiên cứu khoa học', 3, 0),
('MAT2316', 'Lập trình C/C++', 3, 0),
('MAT2317', 'Lập trình Java', 3, 0),
('MAT2318', 'Lập trình Python', 3, 0),
('MAT2319', 'Lập trình Julia', 3, 0),
('MAT2323', 'Xác suất - Thống kê', 4, 0),
('MAT2400', 'Đại số tuyến tính', 5, 0),
('MAT2403', 'Phương trình vi phân', 3, 0),
('MAT2404', 'Giải tích số', 4, 0),
('MAT2405', 'Xác suất', 3, 0),
('MAT2406', 'Thống kê ứng dụng', 4, 0),
('MAT2407', 'Tối ưu hóa', 3, 0),
('MAT2501', 'Giải tích 1', 4, 0),
('MAT2502', 'Giải tích 2', 4, 0),
('MAT2503', 'Giải tích 3', 2, 0),
('MAT2506', 'Kĩ năng mềm', 2, 0),
('MAT3148', 'Tính toán song song', 3, 0),
('MAT3300', 'Đại số đại cương', 4, 0),
('MAT3301', 'Giải tích hàm', 3, 0),
('MAT3302', 'Toán rời rạc', 4, 0),
('MAT3304', 'Thực hành tính toán', 2, 0),
('MAT3305', 'Tôpô đại cương', 3, 0),
('MAT3306', 'Cơ sở hình học vi phân', 3, 0),
('MAT3307', 'Lý thuyết độ đo và tích phân', 3, 0),
('MAT3310', 'Cơ sở tôpô đại số', 3, 0),
('MAT3311', 'Lý thuyết nhóm và biểu diễn nhóm', 3, 0),
('MAT3312', 'Hình học đại số', 3, 0),
('MAT3313', 'Lý thuyết số', 3, 0),
('MAT3314', 'Tôpô vi phân', 3, 0),
('MAT3315', 'Không gian véctơ tôpô', 3, 0),
('MAT3316', 'Giải tích phổ toán tử', 3, 0),
('MAT3317', 'Phương trình đạo hàm riêng 2', 3, 0),
('MAT3318', 'Giải tích trên đa tạp', 3, 0),
('MAT3320', 'Phương trình tích phân', 3, 0),
('MAT3321', 'Quá trình ngẫu nhiên', 3, 0),
('MAT3322', 'Xác suất 2', 3, 0),
('MAT3323', 'Tối ưu rời rạc', 3, 0),
('MAT3324', 'Tổ hợp', 3, 0),
('MAT3325', 'Lịch sử toán học', 3, 0),
('MAT3326', 'Xêmina Toán lý thuyết', 3, 0),
('MAT3327', 'Điều khiển tối ưu', 3, 0),
('MAT3328', 'Phương pháp Monte-Carlo', 3, 0),
('MAT3329', 'Giải tích số 2', 3, 0),
('MAT3333', 'Các mô hình toán ứng dụng 1', 3, 0),
('MAT3334', 'Các mô hình toán ứng dụng 2', 3, 0),
('MAT3335', 'Đại số máy tính', 3, 0),
('MAT3336', 'Lý thuyết mật mã và an toàn thông tin', 3, 0),
('MAT3337', 'Xêmina Toán ứng dụng', 3, 0),
('MAT3339', 'Đại số tuyến tính 3', 3, 0),
('MAT3344', 'Giải tích phức', 4, 0),
('MAT3345', 'Lý thuyết ổn định của phương trình vi phân', 3, 0),
('MAT3346', 'Lý thuyết ước lượng và Kiểm định giả thiết', 3, 0),
('MAT3347', 'Lý thuyết Galois', 4, 0),
('MAT3359', 'Thực tập chuyên ngành', 3, 0),
('MAT3360', 'Tối ưu hoá nâng cao', 3, 0),
('MAT3361', 'Cơ học lý thuyết nâng cao', 3, 0),
('MAT3362', 'Một số vấn đề chọn lọc trong  Cơ học', 3, 0),
('MAT3365', 'Phương trình đạo hàm riêng', 3, 0),
('MAT3366', 'Hệ thống máy tính', 3, 0),
('MAT3367', 'Đại số ứng dụng', 3, 0),
('MAT3368', 'Thuật toán ngẫu nhiên', 3, 0),
('MAT3369', 'Giải tích số nâng cao', 3, 0),
('MAT3370', 'Thống kê Bayes', 3, 0),
('MAT3371', 'Xây dựng phần mềm', 3, 0),
('MAT3372', 'Các thành phần phần mềm', 3, 0),
('MAT3373E', 'Nhập môn an toàn máy tính', 3, 0),
('MAT3374', 'Thực tập thực tế phát triển phần mềm', 3, 0),
('MAT3377', 'Một số vấn đề chọn lọc về Trí tuệ nhân tạo', 3, 0),
('MAT3378', 'Quản trị dữ liệu lớn', 3, 0),
('MAT3379', 'Phân tích hồi quy và ứng dụng', 3, 0),
('MAT3380', 'Seminar Một số vấn đề chọn lọc về Khoa học dữ liệu', 2, 0),
('MAT3381', 'Thực tập thực tế về Khoa học dữ liệu', 3, 0),
('MAT3382', 'Lập trình cho Khoa học dữ liệu', 2, 0),
('MAT3383', 'Trực quan hóa thông tin', 2, 0),
('MAT3384', 'Tự động hóa', 2, 0),
('MAT3385', 'Cơ sở dữ liệu Web và hệ thống thông tin', 3, 0),
('MAT3386', 'Phương pháp tính toán trong thống kê và khoa học d', 3, 0),
('MAT3387', 'Kĩ thuật lấy mẫu khảo sát', 3, 0),
('MAT3388', 'Phân tích chuỗi thời gian', 3, 0),
('MAT3389', 'Quy hoạch thực nghiệm', 3, 0),
('MAT3390', 'Nhập môn Tin sinh học', 3, 0),
('MAT3391', 'Hệ thống thông tin địa lí', 3, 0),
('MAT3392', 'Ứng dụng dữ liệu lớn trong quản lí rủi ro tai biến', 3, 0),
('MAT3393', 'Khai thác dữ liệu trong Hóa học', 3, 0),
('MAT3394', 'Mô hình toán sinh thái', 3, 0),
('MAT3395', 'Lí thuyết trò chơi', 3, 0),
('MAT3397', 'Một số vấn đề ứng dụng của khoa học dữ liệu', 3, 0),
('MAT3398', 'Một số chủ đề trong mô hình hóa và phân tích dữ li', 4, 0),
('MAT3399', 'Xử lí ngôn ngữ tự nhiên và học sâu', 3, 0),
('MAT3401', 'Phép tính biến phân', 3, 0),
('MAT3405', 'Sức bền vật liệu', 3, 0),
('MAT3406', 'Lý thuyết dao động', 3, 0),
('MAT3407', 'Lý thuyết đàn hồi', 3, 0),
('MAT3408', 'Cơ học chất lỏng', 3, 0),
('MAT3409', 'Giải tích hàm ứng dụng', 3, 0),
('MAT3411', 'Phương pháp phần tử hữu hạn', 3, 0),
('MAT3412', 'Lý thuyết dẻo', 3, 0),
('MAT3413', 'Cơ học giải tích', 3, 0),
('MAT3415', 'Cơ học vật liệu composite', 3, 0),
('MAT3416', 'Cơ học kết cấu', 3, 0),
('MAT3417', 'Lý thuyết ổn định chuyển động', 3, 0),
('MAT3418', 'Phương pháp số trong cơ học', 3, 0),
('MAT3419', 'Động lực học chất lỏng nhiều pha', 3, 0),
('MAT3420', 'Lý thuyết chảy rối', 3, 0),
('MAT3422', 'Lý thuyết bản và vỏ mỏng', 4, 0),
('MAT3423', 'Cơ học môi trường liên tục', 3, 0),
('MAT3452', 'Phân tích thống kê nhiều chiều', 3, 0),
('MAT3453', 'Phương pháp chọn mẫu dữ liệu', 3, 0),
('MAT3456', 'Logic ứng dụng', 3, 0),
('MAT3500', 'Toán rời rạc', 4, 0),
('MAT3504', 'Thiết kế và đánh giá thuật toán', 3, 0),
('MAT3505', 'Kiến trúc máy tính', 3, 0),
('MAT3506', 'Mạng máy tính', 3, 0),
('MAT3507', 'Cơ sở dữ liệu', 4, 0),
('MAT3508', 'Nhập môn trí tuệ nhân tạo', 3, 0),
('MAT3509', 'Ngôn ngữ hình thức và ôtômat', 3, 0),
('MAT3514', 'Cấu trúc dữ liệu và thuật toán', 4, 0),
('MAT3518', 'Lập trình hướng đối tượng', 3, 0),
('MAT3519', 'Ngôn ngữ lập trình thứ hai', 2, 0),
('MAT3525', 'Thực hành tính toán', 2, 0),
('MAT3531', 'Tính toán phân tán', 3, 0),
('MAT3532', 'Tính toán song song', 3, 0),
('MAT3533', 'Học máy', 3, 0),
('MAT3534', 'Khai phá dữ liệu', 3, 0),
('MAT3535', 'Tìm kiếm thông tin', 3, 0),
('MAT3538', 'Các hệ thống tri thức', 3, 0),
('MAT3539', 'Mật mã và an toàn dữ liệu', 3, 0),
('MAT3540', 'Cơ sở dữ liệu đa phương tiện', 3, 0),
('MAT3541E', 'Nguyên lí các ngôn ngữ lập trình', 3, 0),
('MAT3542', 'Phát triển ứng dụng web', 3, 0),
('MAT3543', 'Công nghệ phần mềm', 3, 0),
('MAT3545', 'Lý thuyết tính toán', 3, 0),
('MAT3550E', 'Nguyên lí hệ điều hành', 3, 0),
('MAT3552E', 'Thiết kế và đánh giá thuật toán', 3, 0),
('MAT3553E', 'Nhập môn Trí tuệ nhân tạo', 4, 0),
('MAT3554E', 'Ngôn ngữ hình thức và ôtômat', 3, 0),
('MAT3557', 'Môi trường lập trình Linux', 2, 0),
('MAT3558', 'Lập trình mobile', 2, 0),
('MAT3559', 'Xây dựng hệ thống nhúng', 2, 0),
('MAT3560', 'Phát triển phần mềm trò chơi', 2, 0),
('MAT3561', 'Xử lý ngôn ngữ tự nhiên và ứng dụng', 3, 0),
('MAT3561E', 'Xử lí ngôn ngữ tự nhiên và ứng dụng', 3, 0),
('MAT3562', 'Thị giác máy tính', 3, 0),
('MAT3562E', 'Thị giác máy tính', 3, 0),
('MAT3563', 'Một số vấn đề chọn lọc về thị giác máy tính', 3, 0),
('MAT3564', 'Nhập môn tương tác người máy', 3, 0),
('MAT3565', 'Nhập môn khai phá các tập dữ liệu lớn', 3, 0),
('MAT3566', 'Xử lí ảnh 3D', 3, 0),
('MAT3567', 'Phân tích và thiết kế hệ thống thông tin', 3, 0),
('MAT4070', 'Khóa luận tốt nghiệp', 7, 0),
('MAT4071', 'Một số vấn đề chọn lọc trong Toán học', 3, 0),
('MAT4072', 'Một số vấn đề chọn lọc trong tính toán khoa học', 4, 0),
('MAT4081', 'Khóa luận tốt nghiệp', 9, 0),
('MAT4082', 'Khóa luận tốt nghiệp', 7, 0),
('MAT4083', 'Khóa luận tốt nghiệp', 7, 0),
('PEC1008', 'Kinh tế chính trị Mác – Lênin', 2, 0),
('PHI1002', 'Chủ nghĩa xã hội khoa học', 2, 0),
('PHI1006', 'Triết học Mác – Lênin', 3, 0),
('PHY1020', 'Nhập môn Robotics', 3, 0),
('PHY1070', 'Nhập môn Internet kết nối vạn vật', 2, 0),
('PHY1100', 'Cơ - Nhiệt', 3, 0),
('PHY1103', 'Điện - Quang', 3, 0),
('POL1001', 'Tư tưởng Hồ Chí Minh', 2, 0),
('THL1057', 'Nhà nước và pháp luật đại cương', 2, 0);

-- --------------------------------------------------------

--
-- Table structure for table `mon_hoc_dot_dang_ky`
--

CREATE TABLE `mon_hoc_dot_dang_ky` (
  `id_dang_ky` int(11) NOT NULL,
  `ma_mon` varchar(15) DEFAULT NULL,
  `ma_so_lop` varchar(30) DEFAULT NULL,
  `ma_dot_yeu_cau` int(11) DEFAULT NULL,
  `ma_dot` int(11) DEFAULT NULL,
  `th_lt` varchar(30) DEFAULT NULL,
  `thu` varchar(2) DEFAULT NULL,
  `phong_hoc` varchar(10) NOT NULL,
  `tiet_bat_dau` int(11) DEFAULT NULL,
  `tiet_ket_thuc` int(11) DEFAULT NULL,
  `so_luong` int(11) DEFAULT NULL,
  `so_luong_da_dang_ky` int(11) DEFAULT NULL,
  `so_luong_con_lai` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `mon_hoc_nganh`
--

CREATE TABLE `mon_hoc_nganh` (
  `ma_mon` varchar(15) NOT NULL,
  `ma_nganh` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `mon_hoc_nganh`
--

INSERT INTO `mon_hoc_nganh` (`ma_mon`, `ma_nganh`) VALUES
('FLF1107', 'KHDL'),
('FLF1107', 'KHMTTT'),
('FLF1107', 'TH'),
('FLF1107', 'TT'),
('GEO1050', 'KHDL'),
('GEO1050', 'KHMTTT'),
('GEO1050', 'TH'),
('GEO1050', 'TT'),
('HIS1001', 'KHDL'),
('HIS1001', 'KHMTTT'),
('HIS1001', 'TH'),
('HIS1001', 'TT'),
('HIS1056', 'KHDL'),
('HIS1056', 'KHMTTT'),
('HIS1056', 'TH'),
('HIS1056', 'TT'),
('INM1000', 'KHDL'),
('INM1000', 'KHMTTT'),
('INM1000', 'TH'),
('INM1000', 'TT'),
('MAT1060', 'KHDL'),
('MAT1060', 'KHMTTT'),
('MAT1060', 'TH'),
('MAT1060', 'TT'),
('MAT2034', 'KHDL'),
('MAT2034', 'KHMTTT'),
('MAT2300', 'TT'),
('MAT2301', 'TT'),
('MAT2302', 'TT'),
('MAT2303', 'TT'),
('MAT2304', 'TT'),
('MAT2308', 'TH'),
('MAT2310', 'TH'),
('MAT2311', 'TH'),
('MAT2314', 'TT'),
('MAT2315', 'KHDL'),
('MAT2315', 'TH'),
('MAT2315', 'TT'),
('MAT2316', 'KHDL'),
('MAT2316', 'TH'),
('MAT2316', 'TT'),
('MAT2317', 'KHDL'),
('MAT2317', 'TH'),
('MAT2317', 'TT'),
('MAT2318', 'KHDL'),
('MAT2318', 'TH'),
('MAT2318', 'TT'),
('MAT2319', 'KHDL'),
('MAT2319', 'TH'),
('MAT2319', 'TT'),
('MAT2323', 'KHDL'),
('MAT2400', 'KHDL'),
('MAT2403', 'KHDL'),
('MAT2404', 'TT'),
('MAT2405', 'TT'),
('MAT2406', 'TT'),
('MAT2407', 'KHDL'),
('MAT2407', 'TH'),
('MAT2407', 'TT'),
('MAT2501', 'KHDL'),
('MAT2502', 'KHDL'),
('MAT2503', 'KHDL'),
('MAT2506', 'KHDL'),
('MAT3148', 'KHDL'),
('MAT3148', 'KHMTTT'),
('MAT3300', 'TH'),
('MAT3301', 'TH'),
('MAT3302', 'TH'),
('MAT3304', 'TH'),
('MAT3305', 'TH'),
('MAT3306', 'TH'),
('MAT3307', 'TH'),
('MAT3310', 'TH'),
('MAT3311', 'TH'),
('MAT3312', 'TH'),
('MAT3313', 'TH'),
('MAT3314', 'TH'),
('MAT3315', 'TH'),
('MAT3316', 'TH'),
('MAT3317', 'TH'),
('MAT3318', 'TH'),
('MAT3320', 'TH'),
('MAT3321', 'TH'),
('MAT3322', 'TH'),
('MAT3323', 'TH'),
('MAT3323', 'TT'),
('MAT3324', 'TH'),
('MAT3325', 'TH'),
('MAT3326', 'TH'),
('MAT3327', 'TH'),
('MAT3327', 'TT'),
('MAT3328', 'TH'),
('MAT3329', 'TH'),
('MAT3333', 'TH'),
('MAT3333', 'TT'),
('MAT3334', 'TH'),
('MAT3334', 'TT'),
('MAT3335', 'TH'),
('MAT3335', 'TT'),
('MAT3336', 'TH'),
('MAT3337', 'TH'),
('MAT3339', 'TH'),
('MAT3344', 'TH'),
('MAT3345', 'TH'),
('MAT3346', 'TH'),
('MAT3347', 'TH'),
('MAT3359', 'TH'),
('MAT3359', 'TT'),
('MAT3360', 'TH'),
('MAT3361', 'TH'),
('MAT3362', 'TH'),
('MAT3365', 'TT'),
('MAT3366', 'TT'),
('MAT3367', 'TT'),
('MAT3368', 'TT'),
('MAT3369', 'TT'),
('MAT3370', 'TT'),
('MAT3371', 'TT'),
('MAT3372', 'KHDL'),
('MAT3372', 'TT'),
('MAT3373E', 'KHMTTT'),
('MAT3374', 'KHMTTT'),
('MAT3377', 'KHMTTT'),
('MAT3378', 'KHDL'),
('MAT3379', 'KHDL'),
('MAT3380', 'KHDL'),
('MAT3381', 'KHDL'),
('MAT3382', 'KHDL'),
('MAT3383', 'KHDL'),
('MAT3384', 'KHDL'),
('MAT3385', 'KHDL'),
('MAT3386', 'KHDL'),
('MAT3387', 'KHDL'),
('MAT3388', 'KHDL'),
('MAT3389', 'KHDL'),
('MAT3390', 'KHDL'),
('MAT3391', 'KHDL'),
('MAT3392', 'KHDL'),
('MAT3393', 'KHDL'),
('MAT3394', 'KHDL'),
('MAT3395', 'KHDL'),
('MAT3397', 'KHDL'),
('MAT3398', 'KHDL'),
('MAT3399', 'KHDL'),
('MAT3401', 'TH'),
('MAT3405', 'TH'),
('MAT3406', 'TH'),
('MAT3407', 'TH'),
('MAT3408', 'TH'),
('MAT3409', 'TT'),
('MAT3411', 'TH'),
('MAT3412', 'TH'),
('MAT3413', 'TH'),
('MAT3415', 'TH'),
('MAT3416', 'TH'),
('MAT3417', 'TH'),
('MAT3418', 'TH'),
('MAT3419', 'TH'),
('MAT3420', 'TH'),
('MAT3422', 'TH'),
('MAT3423', 'TH'),
('MAT3452', 'KHMTTT'),
('MAT3452', 'TT'),
('MAT3453', 'KHMTTT'),
('MAT3456', 'TT'),
('MAT3500', 'KHDL'),
('MAT3500', 'KHMTTT'),
('MAT3500', 'TT'),
('MAT3504', 'KHDL'),
('MAT3504', 'TT'),
('MAT3505', 'KHMTTT'),
('MAT3506', 'KHMTTT'),
('MAT3507', 'KHDL'),
('MAT3507', 'KHMTTT'),
('MAT3507', 'TT'),
('MAT3508', 'KHDL'),
('MAT3508', 'TT'),
('MAT3509', 'TT'),
('MAT3514', 'KHDL'),
('MAT3514', 'KHMTTT'),
('MAT3514', 'TT'),
('MAT3518', 'KHMTTT'),
('MAT3519', 'KHMTTT'),
('MAT3525', 'TT'),
('MAT3531', 'TT'),
('MAT3532', 'TT'),
('MAT3533', 'KHDL'),
('MAT3533', 'KHMTTT'),
('MAT3533', 'TT'),
('MAT3534', 'KHDL'),
('MAT3534', 'KHMTTT'),
('MAT3535', 'KHDL'),
('MAT3535', 'KHMTTT'),
('MAT3538', 'KHMTTT'),
('MAT3539', 'KHMTTT'),
('MAT3539', 'TT'),
('MAT3540', 'KHMTTT'),
('MAT3541E', 'KHMTTT'),
('MAT3542', 'KHMTTT'),
('MAT3543', 'KHMTTT'),
('MAT3545', 'TT'),
('MAT3550E', 'KHMTTT'),
('MAT3552E', 'KHMTTT'),
('MAT3553E', 'KHMTTT'),
('MAT3554E', 'KHMTTT'),
('MAT3557', 'KHDL'),
('MAT3557', 'KHMTTT'),
('MAT3558', 'KHMTTT'),
('MAT3559', 'KHMTTT'),
('MAT3560', 'KHMTTT'),
('MAT3561', 'TT'),
('MAT3561E', 'KHMTTT'),
('MAT3562', 'KHDL'),
('MAT3562', 'TT'),
('MAT3562E', 'KHMTTT'),
('MAT3563', 'KHMTTT'),
('MAT3564', 'KHMTTT'),
('MAT3565', 'TT'),
('MAT3566', 'KHMTTT'),
('MAT3567', 'KHMTTT'),
('MAT4070', 'TH'),
('MAT4071', 'TH'),
('MAT4072', 'TH'),
('MAT4072', 'TT'),
('MAT4081', 'KHMTTT'),
('MAT4082', 'TT'),
('MAT4083', 'KHDL'),
('PEC1008', 'KHDL'),
('PEC1008', 'KHMTTT'),
('PEC1008', 'TH'),
('PEC1008', 'TT'),
('PHI1002', 'KHDL'),
('PHI1002', 'KHMTTT'),
('PHI1002', 'TH'),
('PHI1002', 'TT'),
('PHI1006', 'KHDL'),
('PHI1006', 'KHMTTT'),
('PHI1006', 'TH'),
('PHI1006', 'TT'),
('PHY1020', 'KHDL'),
('PHY1020', 'KHMTTT'),
('PHY1020', 'TH'),
('PHY1020', 'TT'),
('PHY1070', 'KHDL'),
('PHY1070', 'KHMTTT'),
('PHY1070', 'TH'),
('PHY1070', 'TT'),
('PHY1100', 'KHDL'),
('PHY1100', 'KHMTTT'),
('PHY1100', 'TH'),
('PHY1100', 'TT'),
('PHY1103', 'KHDL'),
('PHY1103', 'KHMTTT'),
('PHY1103', 'TH'),
('PHY1103', 'TT'),
('POL1001', 'KHDL'),
('POL1001', 'KHMTTT'),
('POL1001', 'TH'),
('POL1001', 'TT'),
('THL1057', 'KHDL'),
('THL1057', 'KHMTTT'),
('THL1057', 'TH'),
('THL1057', 'TT');

-- --------------------------------------------------------

--
-- Table structure for table `nganh`
--

CREATE TABLE `nganh` (
  `ma_nganh` varchar(20) NOT NULL,
  `ma_khoa` varchar(20) NOT NULL,
  `ten_nganh` varchar(100) DEFAULT NULL,
  `hinh_thuc_dao_tao` varchar(30) DEFAULT NULL,
  `ma_he` varchar(5) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nganh`
--

INSERT INTO `nganh` (`ma_nganh`, `ma_khoa`, `ten_nganh`, `hinh_thuc_dao_tao`, `ma_he`, `is_delete`) VALUES
('KHDL', 'TCT', 'Khoa học dữ liệu', 'Chính Quy', 'HC', 0),
('KHMTTT', 'TCT', 'Khoa học máy tính và thông tin', 'Chính Quy', 'HC', 0),
('TH', 'TCT', 'Toán Học', 'Chính Quy', 'HC', 0),
('TT', 'TCT', 'Toán Tin', 'Chính Quy', 'HC', 0);

-- --------------------------------------------------------

--
-- Table structure for table `nguoi_quan_li`
--

CREATE TABLE `nguoi_quan_li` (
  `ma_nguoi_quan_li` int(11) NOT NULL,
  `ho_ten` varchar(70) DEFAULT NULL,
  `id_image` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nguoi_quan_li`
--

INSERT INTO `nguoi_quan_li` (`ma_nguoi_quan_li`, `ho_ten`, `id_image`) VALUES
(1510560001, 'Administrator', 'none_image_profile');

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

CREATE TABLE `role` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) DEFAULT NULL,
  `role_path` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`role_id`, `role_name`, `role_path`) VALUES
(1, 'Admin', ''),
(2, 'Người Quản Lý', 'agent/'),
(3, 'Sinh Viên', 'student/');

-- --------------------------------------------------------

--
-- Table structure for table `role_user`
--

CREATE TABLE `role_user` (
  `id_user` int(11) NOT NULL,
  `role_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `role_user`
--

INSERT INTO `role_user` (`id_user`, `role_id`) VALUES
(1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `sinh_vien`
--

CREATE TABLE `sinh_vien` (
  `ma_sinh_vien` int(11) NOT NULL,
  `ho_ten` varchar(70) DEFAULT NULL,
  `gioi_tinh` varchar(4) DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `noi_sinh` varchar(100) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `dan_toc` varchar(15) DEFAULT NULL,
  `dia_chi` varchar(100) DEFAULT NULL,
  `so_dien_thoai` varchar(20) DEFAULT NULL,
  `quoc_tich` varchar(25) DEFAULT NULL,
  `chung_minh_thu` varchar(20) DEFAULT NULL,
  `ngay_cmt` date DEFAULT NULL,
  `noi_cmt` varchar(50) DEFAULT NULL,
  `id_image` varchar(50) DEFAULT 'none_image_profile',
  `is_delete` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `created_by` varchar(70) DEFAULT NULL,
  `update_at` datetime DEFAULT current_timestamp(),
  `update_by` varchar(70) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `sinh_vien`
--

INSERT INTO `sinh_vien` (`ma_sinh_vien`, `ho_ten`, `gioi_tinh`, `ngay_sinh`, `noi_sinh`, `email`, `dan_toc`, `dia_chi`, `so_dien_thoai`, `quoc_tich`, `chung_minh_thu`, `ngay_cmt`, `noi_cmt`, `id_image`, `is_delete`, `created_at`, `created_by`, `update_at`, `update_by`) VALUES
(20002055, 'Nguyễn Khắc Huy', 'Nam', '2002-07-31', 'Đan Phượng', 'khachuynguyen@gmail.com', 'None', 'Đan Phượng', 'None', 'None', 'None', '0000-00-00', 'Đan Phượng', 'none_image_profile', 0, '2022-12-27 20:35:35', 'Administrator', '2022-12-28 14:58:29', 'Administrator'),
(20002062, 'Phạm Như Khoa', 'Nam', '2002-11-08', 'Hoài Đức', 'phamnhuga@gmail.com', 'Kinh', 'Hoài Đức', '0937718364', 'Việt Nam', '001293748284', '2020-08-03', 'Hoài Đức', 'none_image_profile', 0, '2022-12-28 08:33:49', 'Administrator', '2022-12-28 08:33:49', NULL),
(20002076, 'Dương Văn Nam', 'Nam', '2002-10-07', 'Bắc Giang', 'duongnam@gmail.com', 'Kinh', 'Bắc Giang', '0967739865', 'Việt Nam', '0028394187', '0000-00-00', '', 'Image_Profile_20002076', 0, '2022-12-27 16:47:00', 'Administrator', '2022-12-27 22:08:03', 'Administrator'),
(20002077, 'Lã Đức Nam', 'Nam', '2002-11-28', NULL, 'namld@gmail.com', 'Kinh', NULL, NULL, NULL, NULL, NULL, NULL, 'none_image_profile', 0, '2022-12-26 16:49:05', 'Administrator', NULL, NULL),
(20002080, 'Phạm Hồng Nghĩa', 'Nam', '2002-10-07', 'Phú Thọ', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'none_image_profile', 0, '2022-12-27 20:35:35', 'Administrator', '2022-12-27 20:35:35', NULL);

--
-- Triggers `sinh_vien`
--
DELIMITER $$
CREATE TRIGGER `insert_new_data_sinh_vien` AFTER INSERT ON `sinh_vien` FOR EACH ROW INSERT INTO gia_dinh(ma_sinh_vien) VALUES (NEW.ma_sinh_vien)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `sinh_vien_lop`
--

CREATE TABLE `sinh_vien_lop` (
  `ma_sinh_vien` int(11) NOT NULL,
  `ma_lop` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `sinh_vien_lop`
--

INSERT INTO `sinh_vien_lop` (`ma_sinh_vien`, `ma_lop`) VALUES
(20002055, 'KHDL2020'),
(20002062, 'KHDL2020'),
(20002076, 'KHDL2020'),
(20002077, 'KHDL2020'),
(20002080, 'KHDL2020');

-- --------------------------------------------------------

--
-- Table structure for table `truong`
--

CREATE TABLE `truong` (
  `ID` int(11) NOT NULL,
  `ten_truong` varchar(100) NOT NULL,
  `dia_chi` varchar(100) NOT NULL,
  `logo_path` varchar(50) NOT NULL,
  `ngay_thanh_lap` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `truong`
--

INSERT INTO `truong` (`ID`, `ten_truong`, `dia_chi`, `logo_path`, `ngay_thanh_lap`) VALUES
(1, 'Trường Đại học Khoa học Tự Nhiên', '334 Đ. Nguyễn Trãi, Thanh Xuân Trung, Thanh Xuân, Hà Nội', 'web/img/favicon.png', '1956-10-15');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(32) DEFAULT NULL,
  `ma_nguoi_dung` int(11) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `register` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id_user`, `username`, `password`, `ma_nguoi_dung`, `last_login`, `register`) VALUES
(1, '1510560001', '21232f297a57a5a743894a0e4a801fc3', 1510560001, NULL, '2022-12-26 16:31:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dang_ky_mon`
--
ALTER TABLE `dang_ky_mon`
  ADD PRIMARY KEY (`id_dang_ky`,`ma_sinh_vien`);

--
-- Indexes for table `diem`
--
ALTER TABLE `diem`
  ADD PRIMARY KEY (`id_diem`);

--
-- Indexes for table `dot_dang_ky`
--
ALTER TABLE `dot_dang_ky`
  ADD PRIMARY KEY (`ma_dot`);

--
-- Indexes for table `dot_yeu_cau_dang_ky`
--
ALTER TABLE `dot_yeu_cau_dang_ky`
  ADD PRIMARY KEY (`ma_dot_yeu_cau`);

--
-- Indexes for table `gia_dinh`
--
ALTER TABLE `gia_dinh`
  ADD PRIMARY KEY (`ma_sinh_vien`);

--
-- Indexes for table `hoc_ky`
--
ALTER TABLE `hoc_ky`
  ADD PRIMARY KEY (`ma_hoc_ky`);

--
-- Indexes for table `image_data`
--
ALTER TABLE `image_data`
  ADD PRIMARY KEY (`id_image`);

--
-- Indexes for table `khoa`
--
ALTER TABLE `khoa`
  ADD PRIMARY KEY (`ma_khoa`);

--
-- Indexes for table `loai_he`
--
ALTER TABLE `loai_he`
  ADD PRIMARY KEY (`ma_he`);

--
-- Indexes for table `lop`
--
ALTER TABLE `lop`
  ADD PRIMARY KEY (`ma_lop`);

--
-- Indexes for table `mon_hoc`
--
ALTER TABLE `mon_hoc`
  ADD PRIMARY KEY (`ma_mon`);

--
-- Indexes for table `mon_hoc_dot_dang_ky`
--
ALTER TABLE `mon_hoc_dot_dang_ky`
  ADD PRIMARY KEY (`id_dang_ky`);

--
-- Indexes for table `mon_hoc_nganh`
--
ALTER TABLE `mon_hoc_nganh`
  ADD PRIMARY KEY (`ma_mon`,`ma_nganh`);

--
-- Indexes for table `nganh`
--
ALTER TABLE `nganh`
  ADD PRIMARY KEY (`ma_nganh`);

--
-- Indexes for table `nguoi_quan_li`
--
ALTER TABLE `nguoi_quan_li`
  ADD PRIMARY KEY (`ma_nguoi_quan_li`);

--
-- Indexes for table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`role_id`);

--
-- Indexes for table `role_user`
--
ALTER TABLE `role_user`
  ADD PRIMARY KEY (`id_user`,`role_id`);

--
-- Indexes for table `sinh_vien`
--
ALTER TABLE `sinh_vien`
  ADD PRIMARY KEY (`ma_sinh_vien`);

--
-- Indexes for table `sinh_vien_lop`
--
ALTER TABLE `sinh_vien_lop`
  ADD PRIMARY KEY (`ma_sinh_vien`,`ma_lop`);

--
-- Indexes for table `truong`
--
ALTER TABLE `truong`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `diem`
--
ALTER TABLE `diem`
  MODIFY `id_diem` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
