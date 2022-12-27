-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 27, 2022 at 03:16 AM
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
  `thang_4` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
-- Table structure for table `hoc_ky`
--

CREATE TABLE `hoc_ky` (
  `ma_hoc_ky` varchar(15) NOT NULL,
  `ten_hoc_ky` varchar(50) DEFAULT NULL,
  `nam_hoc` year(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
('TCT', 'Toán - Cơ - Tin học');

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
('KHDL2020', 'KHDL', 2020, 'K65A5-Khoa học dữ liệu', NULL, 0);

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
('KHDL', 'TCT', 'Khoa học dữ liệu', 'Chính Quy', 'HC', 0);

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
  `id_image` varchar(50) DEFAULT NULL,
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
(20002077, 'Lã Đức Nam', 'Nam', '2002-11-28', NULL, 'namld@gmail.com', 'Kinh', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2022-12-26 16:49:05', 'Administrator', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `sinh_vien_lop`
--

CREATE TABLE `sinh_vien_lop` (
  `ma_sinh_vien` int(11) NOT NULL,
  `ma_lop` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
  MODIFY `id_diem` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
