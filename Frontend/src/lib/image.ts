/* Perkecil & kompres gambar menu di browser sebelum diunggah (data URL JPEG), supaya muat di batas server
   dan tidak membuat setiap pemuatan data jadi berat. */
export const MAX_IMAGE_CHARS = 380_000
const MAX_SIDE = 640

function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error("Gambar tidak dapat dibaca. Pilih file JPG, PNG, atau WebP."))
    }
    img.src = url
  })
}

export async function compressImage(file: File): Promise<string> {
  if (!file.type.startsWith("image/")) throw new Error("File yang dipilih bukan gambar.")
  const img = await loadImage(file)
  const sourceWidth = img.naturalWidth || img.width
  const sourceHeight = img.naturalHeight || img.height
  if (!sourceWidth || !sourceHeight) throw new Error("Gambar tidak dapat dibaca.")
  let side = MAX_SIDE
  for (let attempt = 0; attempt < 4; attempt++) {
    const scale = Math.min(1, side / Math.max(sourceWidth, sourceHeight))
    const canvas = document.createElement("canvas")
    canvas.width = Math.max(1, Math.round(sourceWidth * scale))
    canvas.height = Math.max(1, Math.round(sourceHeight * scale))
    const context = canvas.getContext("2d")
    if (!context) throw new Error("Browser tidak mendukung pemrosesan gambar.")
    context.fillStyle = "#ffffff" // PNG transparan -> latar putih (JPEG tidak punya alpha)
    context.fillRect(0, 0, canvas.width, canvas.height)
    context.drawImage(img, 0, 0, canvas.width, canvas.height)
    const quality = [0.8, 0.7, 0.6, 0.5][attempt]
    const dataUrl = canvas.toDataURL("image/jpeg", quality)
    if (dataUrl.length <= MAX_IMAGE_CHARS) return dataUrl
    side = Math.round(side * 0.75)
  }
  throw new Error("Gambar terlalu besar. Pilih gambar yang lebih kecil.")
}

/* Pengganti bila menu tidak punya gambar (tanpa bergantung pada CDN luar). */
export const PLACEHOLDER_IMAGE =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect width="400" height="300" fill="#e9ecef"/><g fill="none" stroke="#9aa3ad" stroke-width="10" stroke-linecap="round"><circle cx="200" cy="150" r="62"/><circle cx="200" cy="150" r="34"/></g></svg>`,
  )
