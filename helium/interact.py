#!/usr/bin/env python3

from pwn import *

p64 = lambda x: util.packing.p64(x, endian='little')
u64 = lambda x: util.packing.u64(x, endian='little')
p32 = lambda x: util.packing.p32(x, endian='little')
u32 = lambda x: util.packing.u32(x, endian='little')

exe = ELF("./challenge")

context.binary = exe
context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']


def conn():
	if args.GDB:
		r = gdb.debug([exe.path])
	elif args.REMOTE:
		r = remote("127.0.0.1", 1911)
	else:
		r = process([exe.path])
	return r

r = conn()


def main():
	buf = r.recv(32)
	pid = buf[:4]
	aslr_leak = buf[4:12]
	loc_186f = buf[12:20]
	zero_8 = buf[20:28]
	zero_4 = buf[28:32]

	print("pid: ", pid)
	print("aslr_leak: ", aslr_leak)
	print("loc_186f: ", loc_186f)
	print("zero_8: ", zero_8)
	print("zero_4: ", zero_4)

	r.interactive()


if __name__ == "__main__":
	main()
