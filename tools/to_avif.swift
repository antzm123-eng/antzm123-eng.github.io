import Foundation
import CoreGraphics
import ImageIO

let args = CommandLine.arguments
guard args.count >= 4 else { print("usage: conv <in> <out> <quality>"); exit(1) }
let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
let q = Double(args[3]) ?? 0.55

let copyright = "© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com"

guard let src = CGImageSourceCreateWithURL(inURL as CFURL, nil),
      var img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    print("READ_FAIL"); exit(2)
}
// 홀수 변이 하나라도 있으면 CoreGraphics 의 AVIF 타일(grid) 인코더가 깨진 파일을 만든다
// (libavif/브라우저는 "Invalid image grid" 로 거부 — Apple 자체 디코더만 조용히 허용해 놓친다).
// 짝수로 잘라 원천 차단한다. 최대 1px 차이라 화질에 영향 없다.
let evenW = img.width - (img.width % 2)
let evenH = img.height - (img.height % 2)
if evenW != img.width || evenH != img.height {
    guard let cropped = img.cropping(to: CGRect(x: 0, y: 0, width: evenW, height: evenH)) else {
        print("CROP_FAIL"); exit(7)
    }
    img = cropped
}
guard let dest = CGImageDestinationCreateWithURL(outURL as CFURL, "public.avif" as CFString, 1, nil) else {
    print("DEST_FAIL"); exit(3)
}
let props: [CFString: Any] = [
    kCGImageDestinationLossyCompressionQuality: q,
    kCGImagePropertyTIFFDictionary: [kCGImagePropertyTIFFCopyright: copyright,
                                     kCGImagePropertyTIFFArtist: "강윤구 (Kang Yungu)"],
    kCGImagePropertyIPTCDictionary: [kCGImagePropertyIPTCCopyrightNotice: copyright,
                                     kCGImagePropertyIPTCByline: "강윤구 (Kang Yungu)"]
]
CGImageDestinationAddImage(dest, img, props as CFDictionary)
if CGImageDestinationFinalize(dest) { print("OK \(img.width)x\(img.height)") } else { print("WRITE_FAIL"); exit(4) }
