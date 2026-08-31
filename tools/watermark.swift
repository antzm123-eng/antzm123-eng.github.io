import Foundation
import CoreGraphics
import CoreText
import ImageIO
import UniformTypeIdentifiers

// 사용법: watermark <입력> <출력> <문구> <크기비율> <불투명도> <여백비율>
let a = CommandLine.arguments
guard a.count >= 4 else { FileHandle.standardError.write("인자 부족\n".data(using:.utf8)!); exit(1) }
let inPath = a[1], outPath = a[2], text = a[3]
let sizeRatio = a.count > 4 ? Double(a[4])! : 0.022
let alpha     = a.count > 5 ? Double(a[5])! : 0.55
let marginR   = a.count > 6 ? Double(a[6])! : 0.030

let url = URL(fileURLWithPath: inPath)
guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    FileHandle.standardError.write("이미지 로드 실패: \(inPath)\n".data(using:.utf8)!); exit(2)
}
let w = img.width, h = img.height
let minSide = Double(min(w, h))

let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
        bytesPerRow: 0, space: cs,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { exit(3) }
ctx.draw(img, in: CGRect(x:0, y:0, width:w, height:h))

// ── 글꼴 ──
let fontSize = minSide * sizeRatio
var font = CTFontCreateWithName("AvenirNext-Medium" as CFString, fontSize, nil)
if CTFontCopyPostScriptName(font) as String != "AvenirNext-Medium" {
    font = CTFontCreateWithName("HelveticaNeue-Medium" as CFString, fontSize, nil)
}
let tracking = fontSize * 0.14   // 자간

func makeLine(_ color: CGColor) -> CTLine {
    let attrs: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): font,
        NSAttributedString.Key(kCTForegroundColorAttributeName as String): color,
        NSAttributedString.Key(kCTKernAttributeName as String): tracking
    ]
    return CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attrs))
}
let white = CGColor(colorSpace: cs, components: [1,1,1, CGFloat(alpha)])!
let shadow = CGColor(colorSpace: cs, components: [0,0,0, CGFloat(alpha * 0.5)])!

let line = makeLine(white)
var ascent: CGFloat = 0, descent: CGFloat = 0
let textW = CTLineGetTypographicBounds(line, &ascent, &descent, nil)

let margin = minSide * marginR
let x = Double(w) - margin - textW + Double(tracking)   // 마지막 글자 자간 보정
let y = margin + Double(descent)

ctx.setShouldAntialias(true)
ctx.setAllowsFontSmoothing(true)
// 그림자 먼저 (밝은 배경에서도 보이게)
ctx.textPosition = CGPoint(x: x + fontSize*0.045, y: y - fontSize*0.045)
CTLineDraw(makeLine(shadow), ctx)
// 본 글자
ctx.textPosition = CGPoint(x: x, y: y)
CTLineDraw(line, ctx)

guard let outImg = ctx.makeImage() else { exit(4) }
let isPNG = outPath.lowercased().hasSuffix(".png")
let type = (isPNG ? UTType.png : UTType.jpeg).identifier as CFString
guard let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: outPath) as CFURL, type, 1, nil) else { exit(5) }
let opts: [CFString: Any] = isPNG ? [:] : [kCGImageDestinationLossyCompressionQuality: 0.80]
CGImageDestinationAddImage(dest, outImg, opts as CFDictionary)
guard CGImageDestinationFinalize(dest) else { exit(6) }
