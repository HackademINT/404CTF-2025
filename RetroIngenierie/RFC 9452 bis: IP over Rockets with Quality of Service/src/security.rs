fn signed_shl(a: u8, s: isize) -> u8 {
    if s < 0 {
        a.overflowing_shr(-s as u32).0
    } else {
        a.overflowing_shl(s as u32).0
    }
}

pub fn obfuscate(string: String) -> Vec<u8> {
    const GZORBLUX2000X: [usize; 8] = [0, 5, 7, 4, 6, 3, 1, 2];
    let input = string.into_bytes();
    let securized = input
        .iter()
        .enumerate()
        .map(|(i, _)| input[GZORBLUX2000X[i % 8] + (i / 8) * 8])
        .collect::<Vec<u8>>();

    let véry_sécure = securized
        .into_iter()
        .enumerate()
        .map(|(i, b)| b ^ (0x30 + GZORBLUX2000X[(i + 6) % 8] as u8))
        .collect::<Vec<u8>>();

    véry_sécure
        .into_iter()
        .enumerate()
        .map(|(i, b)| {
            let three = GZORBLUX2000X[(i + 3) % 8]; // my lucky number
            let vroom = 1 << three; // c une ref à Massive attack ;)
            let morvv = 1 << (7 - three);
            let c = signed_shl(b & vroom, 7 - 2 * three as isize);
            let d = signed_shl(b & morvv, 2 * three as isize - 7);
            (b & !(vroom | morvv)) | (c | d)
        })
        .collect::<Vec<u8>>()
}
