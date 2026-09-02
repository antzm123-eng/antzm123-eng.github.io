// 사진의 일부를 정확히 잘라낸다.
//
// 왜 필요한가
//   macOS 의 sips 에도 자르기가 있지만 --cropOffset 이 조용히 무시되고
//   언제나 "가운데"를 잘라낸다. 워터마크는 오른쪽 아래에 있으므로
//   가운데 자르기로는 지워지지 않는다. 그래서 직접 만든다.
//
// 사용법
//   crop <입력> <출력> <x> <y> <폭> <높이> [JPEG 품질 0~1]
//   좌표는 왼쪽 위가 (0,0) 이다. 출력 이름이 .png 면 PNG 로 저장한다.

import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func fail(_ msg: String, _ code: Int32) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(code)
}

let a = CommandLine.arguments
guard a.count >= 7,
      let x = Int(a[3]), let y = Int(a[4]),
      let cw = Int(a[5]), let ch = Int(a[6]) else {
    fail("사용법: crop <입력> <출력> <x> <y> <폭> <높이> [품질]", 1)
}
let inPath = a[1], outPath = a[2]
let quality = a.count > 7 ? (Double(a[7]) ?? 0.92) : 0.92

guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: inPath) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    fail("이미지를 열지 못했습니다: \(inPath)", 2)
}
guard x >= 0, y >= 0, cw > 0, ch > 0,
      x + cw <= img.width, y + ch <= img.height else {
    fail("자를 범위가 사진 밖입니다: 사진 \(img.width)x\(img.height), 요청 \(x),\(y) \(cw)x\(ch)", 3)
}
guard let out = img.cropping(to: CGRect(x: x, y: y, width: cw, height: ch)) else {
    fail("자르기 실패", 4)
}

let isPNG = outPath.lowercased().hasSuffix(".png")
let type = (isPNG ? UTType.png : UTType.jpeg).identifier as CFString
guard let dest = CGImageDestinationCreateWithURL(
        URL(fileURLWithPath: outPath) as CFURL, type, 1, nil) else {
    fail("저장할 곳을 만들지 못했습니다: \(outPath)", 5)
}
let opts: [CFString: Any] = isPNG ? [:] : [kCGImageDestinationLossyCompressionQuality: quality]
CGImageDestinationAddImage(dest, out, opts as CFDictionary)
guard CGImageDestinationFinalize(dest) else { fail("저장 실패: \(outPath)", 6) }
print("\(out.width)x\(out.height)")
