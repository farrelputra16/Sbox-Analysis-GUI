import numpy as np

def hamming_weight(x):
    """Menghitung jumlah bit '1' dalam representasi biner dari x."""
    return bin(x).count('1')

def truth_table(sbox, n, m):
    """Membuat tabel kebenaran untuk fungsi Boolean dari S-box."""
    table = []
    for output_bit in range(m):
        column = []
        for x in range(2**n):
            fx = (sbox[x] >> output_bit) & 1  # Ambil bit tertentu dari output S-box
            column.append(fx)
        table.append(column)
    return np.array(table)

def walsh_transform(f):
    """Menghitung Walsh Transform untuk fungsi Boolean."""
    n = len(f).bit_length() - 1
    W = np.array(f) * 2 - 1  # Ubah 0 menjadi -1
    for i in range(n):
        step = 2**(i + 1)
        for j in range(0, len(f), step):
            for k in range(2**i):
                a, b = W[j + k], W[j + k + 2**i]
                W[j + k], W[j + k + 2**i] = a + b, a - b
    return W

def nonlinearity(sbox, n, m):
    """Menghitung nonlinearity dari S-box."""
    table = truth_table(sbox, n, m)
    min_distance = float('inf')
    for column in table:
        W = walsh_transform(column)
        max_walsh = np.max(np.abs(W))
        distance = 2**(n - 1) - max_walsh / 2
        min_distance = min(min_distance, distance)
    return min_distance

def sac(sbox, n):
    """Menghitung Strict Avalanche Criterion (SAC)."""
    total = 0
    for i in range(2**n):
        original = sbox[i]
        for bit in range(n):
            flipped_input = i ^ (1 << bit)  # Membalikkan satu bit
            flipped_output = sbox[flipped_input]
            diff = original ^ flipped_output
            total += hamming_weight(diff)
    return total / (n * 2**n * n)

def bic_nl(sbox, n):
    """Menghitung Bit Independence Criterion—Nonlinearity (BIC-NL)."""
    total_nl = 0
    count = 0
    for bit1 in range(n):
        for bit2 in range(bit1 + 1, n):  # Bit-bit independen
            count += 1
            sbox_bit1 = [(x >> bit1) & 1 for x in sbox]
            sbox_bit2 = [(x >> bit2) & 1 for x in sbox]

            # Kombinasi kedua bit
            combined = [b1 ^ b2 for b1, b2 in zip(sbox_bit1, sbox_bit2)]
            W = walsh_transform(combined)
            max_walsh = np.max(np.abs(W))
            total_nl += 2**(n - 1) - max_walsh / 2
    s = total_nl / count
    return s

def lap(sbox, n):
    """Menghitung Linear Approximation Probability (LAP)."""
    max_bias = 0
    for a in range(1, 2**n):
        for b in range(1, 2**n):
            bias = 0
            for x in range(2**n):
                input_parity = hamming_weight(x & a) % 2
                output_parity = hamming_weight(sbox[x] & b) % 2
                if input_parity == output_parity:
                    bias += 1
            bias = abs(bias - 2**(n - 1)) / 2**n
            max_bias = max(max_bias, bias)
    return max_bias

def dap(sbox, n):
    """Menghitung Differential Approximation Probability (DAP)."""
    max_diff_prob = 0
    for dx in range(1, 2**n):
        for dy in range(1, 2**n):
            count = 0
            for x in range(2**n):
                if sbox[x ^ dx] ^ sbox[x] == dy:
                    count += 1
            prob = count / 2**n
            max_diff_prob = max(max_diff_prob, prob)
    return max_diff_prob

def bic_sac(sbox):
    n = len(sbox)
    bit_length = 8  # Panjang bit dalam setiap elemen S-box (8 bit untuk AES)
    total_pairs = 0
    total_independence = 0

    for i in range(bit_length):
        for j in range(i + 1, bit_length):  # Hanya pasangan unik
            independence_sum = 0

            for x in range(n):
                for bit_to_flip in range(bit_length):
                    flipped_x = x ^ (1 << bit_to_flip)

                    y1 = sbox[x]
                    y2 = sbox[flipped_x]

                    b1_i = (y1 >> i) & 1
                    b1_j = (y1 >> j) & 1

                    b2_i = (y2 >> i) & 1
                    b2_j = (y2 >> j) & 1

                    independence_sum += ((b1_i ^ b2_i) ^ (b1_j ^ b2_j))

            pair_independence = independence_sum / (n * bit_length)
            total_independence += pair_independence
            total_pairs += 1

    bic_sac = total_independence / total_pairs
    return round(bic_sac, 5)

