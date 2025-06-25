"""Tests for archive processing functions."""

import os
import tempfile

import pytest

from basic_open_agent_tools.data.archive_processing import (
    add_to_archive,
    create_tar_archive,
    create_zip_archive,
    extract_tar_archive,
    extract_zip_archive,
    list_archive_contents,
    validate_archive_integrity,
)
from basic_open_agent_tools.exceptions import DataError


class TestCreateZipArchive:
    """Tests for create_zip_archive function."""

    def test_create_zip_archive_list(self):
        """Test creating a ZIP archive from a list of files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file1_path, file2_path], archive_path)

            # Verify archive was created
            assert os.path.exists(archive_path)
            assert os.path.getsize(archive_path) > 0

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2
            assert any(item["name"] == "file1.txt" for item in contents)
            assert any(item["name"] == "file2.txt" for item in contents)

    def test_create_zip_archive_dict(self):
        """Test creating a ZIP archive from a dictionary mapping."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create ZIP archive with custom paths
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive(
                {file1_path: "docs/file1.txt", file2_path: "docs/file2.txt"},
                archive_path,
            )

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2
            assert any(item["name"] == "docs/file1.txt" for item in contents)
            assert any(item["name"] == "docs/file2.txt" for item in contents)

    def test_create_zip_archive_file_not_found(self):
        """Test creating a ZIP archive with non-existent files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = os.path.join(temp_dir, "archive.zip")

            # Test with list
            with pytest.raises(FileNotFoundError):
                create_zip_archive(["nonexistent.txt"], archive_path)

            # Test with dict
            with pytest.raises(FileNotFoundError):
                create_zip_archive({"nonexistent.txt": "file.txt"}, archive_path)


class TestExtractZipArchive:
    """Tests for extract_zip_archive function."""

    def test_extract_zip_archive(self):
        """Test extracting a ZIP archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file1_path, file2_path], archive_path)

            # Extract archive
            extract_dir = os.path.join(temp_dir, "extracted")
            extracted_files = extract_zip_archive(archive_path, extract_dir)

            # Verify extraction
            assert len(extracted_files) == 2
            assert "file1.txt" in extracted_files
            assert "file2.txt" in extracted_files
            assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
            assert os.path.exists(os.path.join(extract_dir, "file2.txt"))

    def test_extract_zip_archive_not_found(self):
        """Test extracting a non-existent ZIP archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = os.path.join(temp_dir, "extracted")

            with pytest.raises(FileNotFoundError):
                extract_zip_archive("nonexistent.zip", extract_dir)


class TestListArchiveContents:
    """Tests for list_archive_contents function."""

    def test_list_zip_contents(self):
        """Test listing contents of a ZIP archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file1_path, file2_path], archive_path)

            # List contents
            contents = list_archive_contents(archive_path)

            # Verify
            assert len(contents) == 2
            assert all(isinstance(item, dict) for item in contents)
            assert all("name" in item for item in contents)
            assert all("size" in item for item in contents)
            assert all("is_dir" in item for item in contents)
            assert all("compressed_size" in item for item in contents)

    def test_list_tar_contents(self):
        """Test listing contents of a TAR archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar")
            create_tar_archive([file1_path, file2_path], archive_path)

            # List contents
            contents = list_archive_contents(archive_path)

            # Verify
            assert len(contents) == 2
            assert all(isinstance(item, dict) for item in contents)
            assert all("name" in item for item in contents)
            assert all("size" in item for item in contents)
            assert all("is_dir" in item for item in contents)
            assert all("mode" in item for item in contents)

    def test_list_archive_not_found(self):
        """Test listing contents of a non-existent archive."""
        with pytest.raises(FileNotFoundError):
            list_archive_contents("nonexistent.zip")

    def test_list_unsupported_format(self):
        """Test listing contents of an unsupported archive format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with unsupported extension
            file_path = os.path.join(temp_dir, "archive.xyz")
            with open(file_path, "w") as f:
                f.write("Not an archive")

            with pytest.raises(DataError):
                list_archive_contents(file_path)


class TestAddToArchive:
    """Tests for add_to_archive function."""

    def test_add_to_zip_archive(self):
        """Test adding a file to a ZIP archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial test file
            file1_path = os.path.join(temp_dir, "file1.txt")
            with open(file1_path, "w") as f:
                f.write("Test file 1 content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file1_path], archive_path)

            # Create new file to add
            file2_path = os.path.join(temp_dir, "file2.txt")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Add file to archive
            add_to_archive(archive_path, file2_path)

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2
            assert any(item["name"] == "file1.txt" for item in contents)
            assert any(item["name"] == "file2.txt" for item in contents)

    def test_add_to_zip_archive_custom_name(self):
        """Test adding a file to a ZIP archive with a custom name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial test file
            file1_path = os.path.join(temp_dir, "file1.txt")
            with open(file1_path, "w") as f:
                f.write("Test file 1 content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file1_path], archive_path)

            # Create new file to add
            file2_path = os.path.join(temp_dir, "file2.txt")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Add file to archive with custom name
            add_to_archive(archive_path, file2_path, "docs/newfile.txt")

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2
            assert any(item["name"] == "file1.txt" for item in contents)
            assert any(item["name"] == "docs/newfile.txt" for item in contents)

    def test_add_to_archive_not_found(self):
        """Test adding a file to a non-existent archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test content")

            with pytest.raises(FileNotFoundError):
                add_to_archive("nonexistent.zip", file_path)

    def test_add_file_not_found(self):
        """Test adding a non-existent file to an archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty archive
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test content")

            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file_path], archive_path)

            with pytest.raises(FileNotFoundError):
                add_to_archive(archive_path, "nonexistent.txt")


class TestCreateTarArchive:
    """Tests for create_tar_archive function."""

    def test_create_tar_archive_list(self):
        """Test creating a TAR archive from a list of files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar")
            create_tar_archive([file1_path, file2_path], archive_path)

            # Verify archive was created
            assert os.path.exists(archive_path)
            assert os.path.getsize(archive_path) > 0

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2
            assert any(item["name"] == "file1.txt" for item in contents)
            assert any(item["name"] == "file2.txt" for item in contents)

    def test_create_tar_archive_with_compression(self):
        """Test creating a compressed TAR archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create compressed TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar.gz")
            create_tar_archive([file1_path, file2_path], archive_path, compression="gz")

            # Verify archive was created
            assert os.path.exists(archive_path)
            assert os.path.getsize(archive_path) > 0

            # Verify archive contents
            contents = list_archive_contents(archive_path)
            assert len(contents) == 2

    def test_create_tar_archive_invalid_compression(self):
        """Test creating a TAR archive with invalid compression."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test content")

            archive_path = os.path.join(temp_dir, "archive.tar")

            with pytest.raises(DataError):
                create_tar_archive([file_path], archive_path, compression="invalid")


class TestExtractTarArchive:
    """Tests for extract_tar_archive function."""

    def test_extract_tar_archive(self):
        """Test extracting a TAR archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("Test file 1 content")
            with open(file2_path, "w") as f:
                f.write("Test file 2 content")

            # Create TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar")
            create_tar_archive([file1_path, file2_path], archive_path)

            # Extract archive
            extract_dir = os.path.join(temp_dir, "extracted")
            extracted_files = extract_tar_archive(archive_path, extract_dir)

            # Verify extraction
            assert len(extracted_files) == 2
            assert "file1.txt" in extracted_files
            assert "file2.txt" in extracted_files
            assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
            assert os.path.exists(os.path.join(extract_dir, "file2.txt"))

    def test_extract_tar_archive_compressed(self):
        """Test extracting a compressed TAR archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            with open(file1_path, "w") as f:
                f.write("Test file 1 content")

            # Create compressed TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar.gz")
            create_tar_archive([file1_path], archive_path, compression="gz")

            # Extract archive
            extract_dir = os.path.join(temp_dir, "extracted")
            extracted_files = extract_tar_archive(archive_path, extract_dir)

            # Verify extraction
            assert len(extracted_files) == 1
            assert "file1.txt" in extracted_files
            assert os.path.exists(os.path.join(extract_dir, "file1.txt"))


class TestValidateArchiveIntegrity:
    """Tests for validate_archive_integrity function."""

    def test_validate_zip_integrity_valid(self):
        """Test validating a valid ZIP archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test content")

            # Create ZIP archive
            archive_path = os.path.join(temp_dir, "archive.zip")
            create_zip_archive([file_path], archive_path)

            # Validate integrity
            assert validate_archive_integrity(archive_path) is True

    def test_validate_tar_integrity_valid(self):
        """Test validating a valid TAR archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("Test content")

            # Create TAR archive
            archive_path = os.path.join(temp_dir, "archive.tar")
            create_tar_archive([file_path], archive_path)

            # Validate integrity
            assert validate_archive_integrity(archive_path) is True

    def test_validate_integrity_invalid(self):
        """Test validating an invalid archive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid archive file
            archive_path = os.path.join(temp_dir, "invalid.zip")
            with open(archive_path, "w") as f:
                f.write("Not a valid archive")

            # Validate integrity
            assert validate_archive_integrity(archive_path) is False

    def test_validate_integrity_not_found(self):
        """Test validating a non-existent archive."""
        assert validate_archive_integrity("nonexistent.zip") is False

    def test_validate_integrity_unsupported_format(self):
        """Test validating an unsupported archive format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with unsupported extension
            file_path = os.path.join(temp_dir, "archive.xyz")
            with open(file_path, "w") as f:
                f.write("Not an archive")

            # Validate integrity
            assert validate_archive_integrity(file_path) is False
