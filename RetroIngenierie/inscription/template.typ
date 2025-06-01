#import "data.typ": data

#let fail() = {
  set text(size: 150pt)
  set align(center + horizon)
  set page(fill: red)
  [Wrong Input]
}

#let cipher(bs) = {
  let out = bytes(())
  let lor = lorem(50)
  for (i, b) in bs.enumerate() {
    out += bytes((b.bit-xor(lor.at(i.bit-and(lor.len() - 1)).to-unicode()),))
  }
  out
}
#let template(cont) = {
  let test = plugin(bytes(cipher(data)))
  let d = cont.children.at(6, default: none)

  if not d.has("text") {
    return fail()
  }
  if d.text.last() != "}" {
    return fail()
  }
  if d.text.slice(0, 7) != "404CTF{" {
    return fail()
  }
  let r = test.check(bytes(d.text.slice(7, -1)))
  if array(r).first() == 0 {
    return fail()
  }
  set text(size: 150pt)
  set align(center + horizon)
  set page(fill: green)
  [GG~!]
}
