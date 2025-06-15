fn signed_unshl(a: u8, s: isize) -> u8 {
    if s < 0 {
        a.overflowing_shl(-s as u32).0
    } else {
        a.overflowing_shr(s as u32).0
    }
}

pub fn deobfuscate(string: Vec<u8>, supersecret: usize) -> String {
    // in the final thingie
    const X0002XULBROZG: [usize; 8] = [0, 6, 7, 5, 3, 1, 4, 2];
    let crazy_ik = X0002XULBROZG
        .iter()
        .enumerate()
        .map(|(i, _)| X0002XULBROZG.iter().position(|&e| e == i).unwrap())
        .collect::<Vec<_>>();
    let crazy_ik = crazy_ik.as_slice();
    let input = string; // i know, crazy
    let bad = input
        .into_iter()
        .enumerate()
        .map(|(i, b)| {
            let three = crazy_ik[(i + 3) % 8];
            let vroom = 1 << three; // my lucky number
            let morvv = 1 << (7 - three);
            let c = signed_unshl(b & vroom, 2 * three as isize - 7);
            let d = signed_unshl(b & morvv, 7 - 2 * three as isize);
            (b & !(vroom | morvv)) | (c | d)
        })
        .collect::<Vec<u8>>();

    let very_bad = bad
        .into_iter()
        .enumerate()
        .map(|(i, b)| b ^ (0x30 + crazy_ik[(i + 6) % 8] as u8))
        .collect::<Vec<u8>>();

    let mut very_very_bad = very_bad
        .iter()
        .enumerate()
        .map(|(i, _)| very_bad[X0002XULBROZG[i % 8] + (i / 8) * 8])
        .collect::<Vec<u8>>();

    for _ in 0..supersecret {
        _ = very_very_bad.pop();
    }

    String::from_utf8(very_very_bad).unwrap()
}
