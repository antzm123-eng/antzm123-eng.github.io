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
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    print("READ_FAIL"); exit(2)
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
