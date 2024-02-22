import io
import zipfile

def create_zip_content(files):
    # Create an in-memory byte stream
    zip_buffer = io.BytesIO()

    # Create a ZipFile object with the in-memory byte stream
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # Add files to the zip file
        for file_name, file_content in files.items():
            zip_file.writestr(file_name, file_content)

    # Rewind the byte stream pointer to the beginning
    zip_buffer.seek(0)

    # Return the zip file content as bytes
    return zip_buffer.getvalue()


# Example usage
files_to_zip = {
    "file1.txt": "This is the content of file1.txt",
    "folder/file2.txt": "This is the content of file2.txt"
}

zip_content = create_zip_content(files_to_zip)

# Now you can use zip_content as needed, for example, you can write it to a file or send it over a network
