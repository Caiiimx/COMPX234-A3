import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd in ("READ", "GET"):
                if len(parts) < 2:
                    print(f"{line}: ERR Invalid command")
                    continue
                key = parts[1]
                op = "R" if cmd == "READ" else "G"
                total_len = 6 + len(key)
                content = f"{op} {key}"
            elif cmd == "PUT":
                if len(parts) < 3:
                    print(f"{line}: ERR Invalid command")
                    continue
                key, value = parts[1], parts[2]
                if len(key) + 1 + len(value) > 970:
                    print(f"{line}: ERR Message too long")
                    continue
                total_len = 7 + len(key) + len(value)
                content = f"P {key} {value}"
            else:
                print(f"{line}: ERR Unknown command")
                continue
            message = f"{total_len:03d} {content}"

            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            sock.sendall(message.encode())
            size_bytes = sock.recv(3)
            if not size_bytes:
                raise ConnectionError("Server disconnected")
            resp_size = int(size_bytes.decode().strip())
            remaining = resp_size - 3
            response_buffer = b""
            while len(response_buffer) < remaining:
                chunk = sock.recv(remaining - len(response_buffer))
                if not chunk:
                    break
                response_buffer += chunk

            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()