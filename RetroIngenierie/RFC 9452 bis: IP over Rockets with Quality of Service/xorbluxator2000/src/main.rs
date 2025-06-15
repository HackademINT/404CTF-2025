use std::{env::args, process::exit};

use aes::{cipher::{block_padding::Pkcs7, BlockEncryptMut, KeyIvInit}, Aes192};
use cbc::Encryptor;

fn signed_shl(a: u8, s: isize) -> u8 {
    if s < 0 {
        a.overflowing_shr(-s as u32).0
    } else {
        a.overflowing_shl(s as u32).0
    }
}

pub fn obfuscate(string: String) -> Vec<u8> {
    const GZORBLUX2000X: [usize;8] = [0, 5, 7, 4, 6, 3, 1, 2];
    let input = string.into_bytes();
    let securized = input
        .iter()
        .enumerate()
        .map(|(i, _)| input[GZORBLUX2000X[i%8] + (i/8) * 8])
        .collect::<Vec<u8>>();

     let véry_sécure = securized
        .into_iter()
        .enumerate()
        .map(|(i, b)| b ^ (0x30 + GZORBLUX2000X[(i+6)%8] as u8))
        .collect::<Vec<u8>>();

    let eunbrékabeule = véry_sécure
        .into_iter()
        .enumerate()
        .map(|(i, b)| {
            let three = GZORBLUX2000X[(i+3)%8]; // my lucky number
            let vroom = 1 << three; // c une ref à Massive attack ;)
            let morvv = 1 << (7 - three);
            //println!("about to {:b} << {}", (b & vroom), (7 - 2*three as isize));
            let c = signed_shl(b & vroom, 7 - 2*three as isize);
            let d = signed_shl(b & morvv, 2*three as isize - 7);
            (b & !(vroom | morvv)) | (c|d)
        })
        .collect::<Vec<u8>>();

    eunbrékabeule
}

fn deobfuscate(string: Vec<u8>, supersecret: usize) -> String {
                                                               // in the final thingie
    const X0002XULBROZG: [usize;8] = [0, 6, 7, 5, 3, 1, 4, 2];
    let crazy_ik = X0002XULBROZG.iter().enumerate().map(|(i, _)| X0002XULBROZG.iter().position(|&e| e == i).expect("impossible")).collect::<Vec<_>>();
    let crazy_ik = crazy_ik.as_slice();
    let input = string; // i know, crazy
    let bad = input
        .into_iter()
        .enumerate()
        .map(|(i, b)| {
            let three = crazy_ik[(i+3)%8];
            let vroom = 1 << three; // my lucky number
            let morvv = 1 << (7 - three);
            let c = signed_shl(b & vroom, 7 - 2*three as isize);
            let d = signed_shl(b & morvv, 2*three as isize - 7);
            (b & !(vroom | morvv)) | (c|d)
        })
        .collect::<Vec<u8>>();
    
    let very_bad = bad
        .into_iter()
        .enumerate()
        .map(|(i, b)| b ^ (0x30 + crazy_ik[(i+6)%8] as u8))
        .collect::<Vec<u8>>();

    let mut very_very_bad = very_bad
        .iter()
        .enumerate()
        .map(|(i, _)| very_bad[X0002XULBROZG[i%8] + (i/8) * 8])
        .collect::<Vec<u8>>();

    for _ in 0..supersecret {
        _ = very_very_bad.pop();
    }

    String::from_utf8(very_very_bad).expect("ono")
}

// (de)obfuscation as a binary ~
fn main() {
    println!("Ladies and gents, welcome, Welcome to Xorbluxator2000X");
    let mut args = args();
    if args.len() != 3 {
        println!("annnnw that's tubad :(");
        exit(8)
    }
    let _ = args.next();
    let method = args.next().expect("wh- how- wha-");
    let mut input = args.next().expect("wh- how- wha- why?");
    match method.as_str() {
        "-flag" | "-s" | "--string" | "s" | "string" => (),
        "-f" | "--file" | "f" | "file" => {
            input = std::fs::read_to_string(input).expect("pleaaase give a real file....");
        },
        _ => {
            println!("woah there handle me in a better way please :(");
            exit(9);
        },
    }
    let mut magic = 0;
    if method != "-flag" {
        if input.len()%8 != 0 {
            for _ in 0..(8 - input.len()%8) {
                magic += 1;
                input.push('f');
            }
        }
    }

    let feldup = obfuscate(input.clone());
    let uno_rev_card = deobfuscate(feldup.clone(), magic);

    if method == "-flag" {
        let sol = [true, false, false, true, true, true, true, false, false, false, false, false, true, true, true, true, true, true, true, true, true, false, false, false, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, false, true, true, true, true, true, true, true, true, true, true, false, false, true, true, true, true, true, true, true, true, true, true, false, false, true, true, true, false, false, false, false, true, true, true, true, false, true, false, false, false, false, false, false, false, false, true, true, true, true, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false];
        let mut a = sol
            .chunks_exact(8)
            .map(|bs| {
                bs.iter()
                    .enumerate()
                    .fold(0, |f, (i, &b)| f + (b as u8) << i)
            })
            .collect::<Vec<u8>>();
        a.append(&mut vec![0; 6]);
        let enc: Encryptor<Aes192> = Encryptor::new(a.as_slice().into(), b"c2tpYmlkaXJpenp6".into());
        let tmp = input.clone();
        let as_slice = tmp.as_bytes();
        let len = as_slice.len();
        let mut buf = [0u8; 128];
        buf[..len].copy_from_slice(&as_slice);
        let cyph = enc.encrypt_padded_mut::<Pkcs7>(&mut buf, len).unwrap();
        print!("Here's an encoded flag! : ");
        println!("{:x?}", cyph); // commentaire de juste avant de mettre ça sur github: oui,
                                 // j'étais fatigué quand j'ai écrit ça Oo
                                 // (mais tout va bien :) )
        exit(0)
    }

    let le_result_au_chocolat = feldup.into_iter().map(|b| b as char).collect::<String>();
    println!("Mon resultat être comme {:?} -> {:?}", le_result_au_chocolat, uno_rev_card);
    print_as_bs(le_result_au_chocolat);
    println!("I'll let you in on a secret: {}", magic)
}

//fn print_hex_bytes(slice: &[u8]) {
//    print!("\"");
//    string
//        .chars()
//        .for_each(|c| print!("\\x{:02x}", c as u8));
//    println!("\"");
//}
fn print_as_bs(string: String) {
    print!("\"");
    string
        .chars()
        .for_each(|c| print!("\\x{:02x}", c as u8));
    println!("\"");
}
