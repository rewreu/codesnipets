#!/bin/bash

# Function to display usage
usage() {
    echo "Usage:"
    echo "  Encrypt: $0 -e <path_to_file_or_folder>"
    echo "  Decrypt: $0 -d <path_to_encrypted_file>"
    exit 1
}

# Ensure an option and path are provided
if [ $# -lt 2 ]; then
    usage
fi

OPTION="$1"
TARGET="$2"

case "$OPTION" in
    -e)
        if [ ! -e "$TARGET" ]; then
            echo "Error: Path '$TARGET' does not exist."
            exit 1
        fi
        
        # Remove trailing slash for clean naming if a directory is passed
        CLEAN_TARGET="${TARGET%/}"
        OUTPUT="${CLEAN_TARGET}.tar.gz.enc"

        # Get parent directory and base target name to maintain clean archive structure
        PARENT_DIR=$(dirname "$CLEAN_TARGET")
        BASE_NAME=$(basename "$CLEAN_TARGET")

        echo "Encrypting '$TARGET' -> '$OUTPUT'..."
        tar -czf - -C "$PARENT_DIR" "$BASE_NAME" | openssl enc -aes-256-cbc -pbkdf2 -e -out "$OUTPUT"

        if [ $? -eq 0 ]; then
            echo "Successfully encrypted: $OUTPUT"
        else
            echo "Encryption failed."
            exit 1
        fi
        ;;

    -d)
        if [ ! -f "$TARGET" ]; then
            echo "Error: Encrypted file '$TARGET' does not exist."
            exit 1
        fi

        echo "Decrypting '$TARGET'..."
        openssl enc -aes-256-cbc -pbkdf2 -d -in "$TARGET" | tar -xzf -

        if [ $? -eq 0 ]; then
            echo "Successfully decrypted and extracted."
        else
            echo "Decryption failed (check your password)."
            exit 1
        fi
        ;;

    *)
        usage
        ;;
esac