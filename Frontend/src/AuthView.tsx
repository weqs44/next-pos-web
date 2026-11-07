import { useEffect, useRef, useState } from "react"
import { Icon } from "./Icon"
import {
  MIN_PASSWORD,
  consumeSessionNotice,
  login,
  logout,
  registerManager,
  resendVerification,
  verifyEmail,
  type Account,
} from "./lib/store"

type Mode = "login" | "register"

export function AuthView({
  onAuthenticated,
}: {
  onAuthenticated: (account: Account) => void
}) {
  const [mode, setMode] = useState<Mode>("login")
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [loginRole, setLoginRole] = useState<"manager" | "cashier">("manager")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [remember, setRemember] = useState(true)
  const [error, setError] = useState("")
  const [notice, setNotice] = useState(() => consumeSessionNotice())
  const [loading, setLoading] = useState(false)
  // Setelah daftar: tampilkan layar "periksa email" (emailSent=false bila SMTP gagal mengirim).
  const [sentTo, setSentTo] = useState<{ email: string; emailSent: boolean } | null>(null)
  // Email manajer yang belum diverifikasi, untuk tombol "Kirim ulang".
  const [needsVerify, setNeedsVerify] = useState("")
  const verifyHandled = useRef(false)

  const registering = mode === "register"

  // Tautan di email berbentuk /?verify=<token>: konfirmasi ke server, lalu bersihkan alamat.
  useEffect(() => {
    if (verifyHandled.current) return
    const token = new URLSearchParams(window.location.search).get("verify")
    if (!token) return
    verifyHandled.current = true
    window.history.replaceState(null, "", window.location.pathname)
    setLoading(true)
    void verifyEmail(token).then((result) => {
      setLoading(false)
      if (result.ok) {
        setError("")
        setNotice("Email berhasil diverifikasi. Silakan masuk.")
        if (result.value) setEmail(result.value)
      } else {
        setError(result.error)
      }
    })
  }, [])

  async function resend(address: string) {
    if (loading) return
    setLoading(true)
    const result = await resendVerification(address)
    setLoading(false)
    if (result.ok) {
      setError("")
      setNotice("Jika email terdaftar dan belum diverifikasi, email verifikasi baru telah dikirim. Periksa juga folder spam.")
    } else {
      setNotice("")
      setError(result.error)
    }
  }

  function switchMode(next: Mode) {
    setMode(next)
    setError("")
    setNotice("")
    setNeedsVerify("")
    setPassword("")
    setConfirm("")
    setEmail("")
    setLoginRole("manager")
  }


  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (loading) return
    setError("")
    setNotice("")
    setNeedsVerify("")
    if (registering && password !== confirm) {
      setError("Konfirmasi kata sandi tidak sama.")
      return
    }
    setLoading(true)
    if (registering) {
      const created = await registerManager({ name, email, password }, remember)
      setLoading(false)
      if (!created.ok) {
        setError(created.error)
        if (created.code === "email_not_verified") setNeedsVerify(email.trim().toLowerCase())
        return
      }
      if (created.value.account) {
        // Verifikasi email dimatikan di server: langsung masuk.
        onAuthenticated(created.value.account)
        return
      }
      setPassword("")
      setConfirm("")
      setSentTo({ email: created.value.email, emailSent: created.value.emailSent })
      return
    }
    const result = await login(email, password, remember)
    setLoading(false)
    if (!result.ok) {
      setError(result.error)
      if (result.code === "email_not_verified") setNeedsVerify(email.trim().toLowerCase())
      return
    }
    if (result.value.role !== loginRole) {
      logout()
      setError(`Akun ini bukan akun ${loginRole === "manager" ? "manajer" : "kasir"}. Pilih jenis akun yang sesuai.`)
      return
    }
    onAuthenticated(result.value)
  }

  return (
    <main className="login-page">
      <section className="login-brand-panel">
        <div className="login-brand">
          <div className="brand-mark">
            <span>N</span>
          </div>
          <strong>NEXT POS</strong>
        </div>
        <div className="login-brand-copy">
          <span className="login-kicker">Point of sale generasi baru</span>
          <h1>Kelola setiap pesanan dalam satu orbit.</h1>
          <p>
            Penjualan, menu, dan aktivitas shift tersinkron dalam ruang kerja
            yang cepat dan mudah digunakan.
          </p>
        </div>
        <div className="login-orbit" aria-hidden="true">
          <span className="orbit-core">N</span>
          <i></i>
          <i></i>
          <i></i>
        </div>
        <div className="login-brand-footer">
          <span>
            <i></i> Sistem operasional
          </span>
          <strong>Online</strong>
        </div>
      </section>

      <section className="login-form-panel">
        <div className="login-mobile-brand">
          <div className="brand-mark">
            <span>N</span>
          </div>
          <strong>NEXT POS</strong>
        </div>
        {sentTo ? (
          <div className="login-form">
            <div className="login-heading">
              <span className="eyebrow">Verifikasi email</span>
              <h2>Periksa email Anda</h2>
              <p>
                {sentTo.emailSent
                  ? `Kami mengirim tautan verifikasi ke ${sentTo.email}. Buka tautan itu lalu masuk. Periksa folder spam bila tidak muncul.`
                  : `Akun dibuat, tetapi email verifikasi ke ${sentTo.email} belum terkirim. Tekan "Kirim ulang email verifikasi".`}
              </p>
            </div>
            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}
            {notice && (
              <div className="login-notice" role="status">
                {notice}
              </div>
            )}
            <button
              className="login-submit"
              disabled={loading}
              onClick={() => void resend(sentTo.email)}
              type="button"
            >
              <span>{loading ? "Mengirim..." : "Kirim ulang email verifikasi"}</span>
            </button>
            <p className="auth-switch">
              Sudah verifikasi?{" "}
              <button
                onClick={() => {
                  setSentTo(null)
                  switchMode("login")
                }}
                type="button"
              >
                Masuk
              </button>
            </p>
          </div>
        ) : (
        <form className="login-form" onSubmit={submit} noValidate>
          <div className="login-heading">
            <span className="eyebrow">
              {registering ? "Pendaftaran" : "Akses pekerja"}
            </span>
            <h2>{registering ? "Buat akun manajer" : "Selamat datang kembali"}</h2>
            <p>
              {registering
                ? "Manajer dapat mendaftarkan kasir dan memantau kinerja shift mereka."
                : "Masuk menggunakan akun pekerja yang telah terdaftar."}
            </p>
          </div>

          {registering && (
            <label className="login-field">
              <span>Nama lengkap</span>
              <div>
                <Icon name="user" size={18} />
                <input
                  autoComplete="name"
                  name="name"
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Nama Anda"
                  value={name}
                />
              </div>
            </label>
          )}

          <label className="login-field">
            <span>{registering ? "Email" : "Email pekerja"}</span>
            <div>
              <Icon name="mail" size={18} />
              <input
                autoComplete="email"
                name="email"
                onChange={(event) => setEmail(event.target.value)}
                placeholder="nama@restoran.id"
                type="email"
                value={email}
              />
            </div>
          </label>

          <label className="login-field">
            <span>Kata sandi</span>
            <div>
              <Icon name="lock" size={18} />
              <input
                autoComplete={registering ? "new-password" : "current-password"}
                name="password"
                onChange={(event) => setPassword(event.target.value)}
                placeholder={
                  registering
                    ? `Minimal ${MIN_PASSWORD} karakter`
                    : "Masukkan kata sandi"
                }
                type={passwordVisible ? "text" : "password"}
                value={password}
              />
              <button
                aria-label={
                  passwordVisible
                    ? "Sembunyikan kata sandi"
                    : "Tampilkan kata sandi"
                }
                className="password-toggle"
                onClick={() => setPasswordVisible((current) => !current)}
                type="button"
              >
                <Icon name="eye" size={17} />
              </button>
            </div>
          </label>

          {registering && (
            <label className="login-field">
              <span>Ulangi kata sandi</span>
              <div>
                <Icon name="shield" size={18} />
                <input
                  autoComplete="new-password"
                  name="confirm-password"
                  onChange={(event) => setConfirm(event.target.value)}
                  placeholder="Ketik ulang kata sandi"
                  type={passwordVisible ? "text" : "password"}
                  value={confirm}
                />
              </div>
            </label>
          )}

          <div className="login-options">
            <label>
              <input
                checked={remember}
                name="remember"
                onChange={(event) => setRemember(event.target.checked)}
                type="checkbox"
              />
              <span>Ingat perangkat ini</span>
            </label>
            {!registering && (
              <button
                onClick={() => {
                  setError("")
                  setNotice(
                    "Hubungi manajer Anda untuk mengatur ulang kata sandi.",
                  )
                }}
                type="button"
              >
                Lupa kata sandi?
              </button>
            )}
          </div>

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}
          {notice && (
            <div className="login-notice" role="status">
              {notice}
            </div>
          )}
          {needsVerify && (
            <p className="auth-switch">
              <button
                disabled={loading}
                onClick={() => void resend(needsVerify)}
                type="button"
              >
                Kirim ulang email verifikasi
              </button>
            </p>
          )}

          <button className="login-submit" disabled={loading} type="submit">
            <span>
              {loading
                ? "Memverifikasi..."
                : registering
                  ? "Buat akun"
                  : "Masuk ke NEXT"}
            </span>
            {!loading && <Icon name="chevron" size={18} />}
          </button>

          <p className="auth-switch">
            {registering ? "Sudah punya akun?" : "Pemilik toko baru?"}{" "}
            <button
              onClick={() => switchMode(registering ? "login" : "register")}
              type="button"
            >
              {registering ? "Masuk" : "Daftar sebagai manajer"}
            </button>
          </p>

          {!registering && (
            <div className="login-role-choice" aria-label="Jenis akun">
              <span>Masuk sebagai</span>
              <div className="login-role-options">
                <button
                  aria-pressed={loginRole === "manager"}
                  className={loginRole === "manager" ? "selected" : ""}
                  onClick={() => setLoginRole("manager")}
                  type="button"
                >
                  Manajer
                </button>
                <button
                  aria-pressed={loginRole === "cashier"}
                  className={loginRole === "cashier" ? "selected" : ""}
                  onClick={() => setLoginRole("cashier")}
                  type="button"
                >
                  Kasir
                </button>
              </div>
              <p>Akun kasir dibuat oleh manajer dari menu Tim.</p>
            </div>
          )}
        </form>
        )}
        <p className="login-legal">
          Dengan masuk, Anda menyetujui kebijakan keamanan tempat kerja.
        </p>
      </section>
    </main>
  )
}
