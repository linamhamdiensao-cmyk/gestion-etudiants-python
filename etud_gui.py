import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    PRIMARY, SECONDARY, SUCCESS, INFO, WARNING, DANGER, LIGHT, DARK, OUTLINE,
)
from ttkbootstrap.dialogs import Messagebox, Querybox
from tkinter import filedialog, messagebox as std_messagebox

from etud import Etudiant, Note, Promotion, Etablissement, GestionFichier, Admin


THEME_LIGHT = "cosmo"
THEME_DARK = "darkly"


# ────────────────── DIALOGUES ──────────────────

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.admin = Admin()
        self.on_success = on_success

        # Centrage vertical
        spacer_top = ttk.Frame(self); spacer_top.pack(expand=True)
        card = ttk.Frame(self, padding=30)
        card.pack()
        spacer_bot = ttk.Frame(self); spacer_bot.pack(expand=True)

        ttk.Label(card, text="Bienvenue", font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        ttk.Label(card, text="Connecte-toi pour continuer",
                  bootstyle="secondary").pack(pady=(0, 20))

        ttk.Label(card, text="Login").pack(anchor="w")
        self.login_entry = ttk.Entry(card, width=32)
        self.login_entry.pack(pady=(2, 12))
        self.login_entry.insert(0, "admin")

        ttk.Label(card, text="Mot de passe").pack(anchor="w")
        self.mdp_entry = ttk.Entry(card, width=32, show="•")
        self.mdp_entry.pack(pady=(2, 18))

        ttk.Button(card, text="Se connecter", bootstyle=PRIMARY,
                   command=self.connect).pack(fill="x", ipady=5)

        master.bind("<Return>", lambda _e: self.connect())
        self.login_entry.focus()

    def connect(self):
        if self.admin.authentifier(self.login_entry.get(), self.mdp_entry.get()):
            self.on_success()
        else:
            Messagebox.show_error("Login ou mot de passe incorrect",
                                  title="Erreur", parent=self)


class _ModalDialog(ttk.Toplevel):
    """Petite base pour les dialogues modaux (Toplevel ttkbootstrap)."""

    def __init__(self, parent, title, width=380, height=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.result = None
        self._build_body(ttk.Frame(self, padding=16))

    def _build_body(self, body):
        body.pack(fill="both", expand=True)
        self.body(body)
        btns = ttk.Frame(self, padding=(16, 0, 16, 16))
        btns.pack(fill="x")
        ttk.Button(btns, text="Annuler", bootstyle=(SECONDARY, OUTLINE),
                   command=self._cancel).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Valider", bootstyle=PRIMARY,
                   command=self._ok).pack(side="right")
        self.bind("<Return>", lambda _e: self._ok())
        self.bind("<Escape>", lambda _e: self._cancel())
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x,0)}+{max(y,0)}")
        self.grab_set()
        self.wait_window(self)

    def _ok(self):
        if self.validate():
            self.apply()
            self.destroy()

    def _cancel(self):
        self.destroy()

    # Surcharger
    def body(self, master): ...
    def validate(self): return True
    def apply(self): ...


class PromotionDialog(_ModalDialog):
    FILIERES = ["IDSCC", "INFO", "CIVIL", "ELEC", "ITIRC"]
    NIVEAUX = [
        "1ère année cycle d'ingénieur",
        "2ème année cycle d'ingénieur",
        "3ème année cycle d'ingénieur",
    ]

    def __init__(self, parent):
        super().__init__(parent, title="Nouvelle promotion")

    def body(self, master):
        ttk.Label(master, text="Filière").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.cb_filiere = ttk.Combobox(master, values=self.FILIERES, state="readonly", width=34)
        self.cb_filiere.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.cb_filiere.current(0)

        ttk.Label(master, text="Niveau").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.cb_niveau = ttk.Combobox(master, values=self.NIVEAUX, state="readonly", width=34)
        self.cb_niveau.grid(row=3, column=0, sticky="ew")
        self.cb_niveau.current(0)

    def validate(self):
        if not self.cb_filiere.get() or not self.cb_niveau.get():
            Messagebox.show_warning("Filière et niveau obligatoires.", parent=self)
            return False
        return True

    def apply(self):
        self.result = (self.cb_filiere.get(), self.cb_niveau.get())


class EtudiantDialog(_ModalDialog):
    def __init__(self, parent):
        super().__init__(parent, title="Nouvel étudiant")

    def body(self, master):
        ttk.Label(master, text="Nom").grid(row=0, column=0, sticky="w")
        self.e_nom = ttk.Entry(master, width=34)
        self.e_nom.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(master, text="Prénom").grid(row=2, column=0, sticky="w")
        self.e_prenom = ttk.Entry(master, width=34)
        self.e_prenom.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(master, text="Age").grid(row=4, column=0, sticky="w")
        self.e_age = ttk.Entry(master, width=34)
        self.e_age.grid(row=5, column=0, sticky="ew", pady=(2, 0))

        self.e_nom.focus()

    def validate(self):
        if not self.e_nom.get().strip() or not self.e_prenom.get().strip():
            Messagebox.show_warning("Nom et prénom obligatoires.", parent=self)
            return False
        try:
            int(self.e_age.get())
        except ValueError:
            Messagebox.show_warning("Age doit être un nombre entier.", parent=self)
            return False
        return True

    def apply(self):
        self.result = {
            "nom": self.e_nom.get().strip(),
            "prenom": self.e_prenom.get().strip(),
            "age": int(self.e_age.get()),
        }


class NoteDialog(_ModalDialog):
    def __init__(self, parent, titre="Nouvelle note"):
        super().__init__(parent, title=titre)

    def body(self, master):
        ttk.Label(master, text="Matière").grid(row=0, column=0, sticky="w")
        self.e_matiere = ttk.Entry(master, width=34)
        self.e_matiere.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(master, text="Note  /20").grid(row=2, column=0, sticky="w")
        self.e_valeur = ttk.Entry(master, width=34)
        self.e_valeur.grid(row=3, column=0, sticky="ew")

        self.e_matiere.focus()

    def validate(self):
        if not self.e_matiere.get().strip():
            Messagebox.show_warning("Matière obligatoire.", parent=self)
            return False
        try:
            v = float(self.e_valeur.get())
            if not 0 <= v <= 20:
                raise ValueError
        except ValueError:
            Messagebox.show_warning("La note doit être un nombre entre 0 et 20.", parent=self)
            return False
        return True

    def apply(self):
        self.result = Note(self.e_matiere.get().strip(), float(self.e_valeur.get()))


# ────────────────── PAGES ──────────────────

class HomeFrame(ttk.Frame):
    def __init__(self, master, etab, on_open):
        super().__init__(master, padding=20)
        self.etab = etab
        self.on_open = on_open
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="📚  Promotions", font=("Segoe UI", 22, "bold")).pack(side="left")

        actions_top = ttk.Frame(header)
        actions_top.pack(side="right")
        ttk.Button(actions_top, text="+ Nouvelle promotion", bootstyle=SUCCESS,
                   command=self._new_promo).pack(side="left", padx=4)
        ttk.Button(actions_top, text="🗑  Supprimer", bootstyle=(DANGER, OUTLINE),
                   command=self._delete_promo).pack(side="left", padx=4)

        ttk.Label(self, text="Sélectionne une promotion (double-clic) ou crée-en une nouvelle.",
                  bootstyle="secondary").pack(anchor="w", pady=(4, 14))

        cols = ("filiere", "niveau", "nb", "moyenne")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 selectmode="browse", bootstyle=PRIMARY, height=14)
        for c, label, w, anchor in [
            ("filiere", "Filière", 140, "w"),
            ("niveau", "Niveau", 320, "w"),
            ("nb", "Étudiants", 110, "center"),
            ("moyenne", "Moyenne /20", 130, "center"),
        ]:
            self.tree.heading(c, text=label)
            self.tree.column(c, width=w, anchor=anchor)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self._open_selected())

        ttk.Button(self, text="Ouvrir la promotion sélectionnée", bootstyle=PRIMARY,
                   command=self._open_selected).pack(fill="x", pady=(14, 0), ipady=4)

        self.refresh()

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for p in self.etab.liste_promotions():
            self.tree.insert("", "end", values=(p.filiere, p.niveau, len(p.etudiants),
                                                f"{p.moyenne_generale():.2f}"))

    def _selected_promo(self):
        sel = self.tree.selection()
        if not sel:
            return None
        filiere, niveau = self.tree.item(sel[0], "values")[:2]
        return self.etab.get(filiere, niveau)

    def _open_selected(self):
        p = self._selected_promo()
        if not p:
            Messagebox.show_info("Sélectionne une promotion.", parent=self)
            return
        self.on_open(p)

    def _new_promo(self):
        dlg = PromotionDialog(self.winfo_toplevel())
        if not dlg.result:
            return
        filiere, niveau = dlg.result
        promo = self.etab.get_or_create(filiere, niveau)
        self.refresh()
        self.on_open(promo)

    def _delete_promo(self):
        p = self._selected_promo()
        if not p:
            return
        if std_messagebox.askyesno(
            "Confirmation",
            f"Supprimer la promotion {p.nom_promotion} et ses {len(p.etudiants)} étudiant(s) ?",
            parent=self.winfo_toplevel(),
        ):
            self.etab.supprimer(p.filiere, p.niveau)
            self.refresh()


class PromotionFrame(ttk.Frame):
    def __init__(self, master, promo, fichiers, on_back):
        super().__init__(master, padding=20)
        self.promo = promo
        self.fichiers = fichiers
        self.on_back = on_back
        self._build()

    def _build(self):
        # En-tête
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Button(top, text="←  Retour", bootstyle=(SECONDARY, OUTLINE),
                   command=self.on_back).pack(side="left")
        ttk.Label(top, text=f"  {self.promo.nom_promotion}",
                  font=("Segoe UI", 18, "bold")).pack(side="left", padx=10)

        # Stat cards
        stats = ttk.Frame(self)
        stats.pack(fill="x", pady=(12, 14))
        self.card_nb = self._make_card(stats, "Étudiants", "0", INFO, 0)
        self.card_moy = self._make_card(stats, "Moyenne générale", "0.00 / 20", SUCCESS, 1)
        self.card_top = self._make_card(stats, "Meilleur étudiant", "—", WARNING, 2)
        for c in range(3):
            stats.columnconfigure(c, weight=1)

        # Tableau
        cols = ("nom", "prenom", "age", "moyenne")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 selectmode="browse", bootstyle=PRIMARY, height=12)
        for c, label, w, anchor in [
            ("nom", "Nom", 200, "w"),
            ("prenom", "Prénom", 200, "w"),
            ("age", "Age", 80, "center"),
            ("moyenne", "Moyenne /20", 130, "center"),
        ]:
            self.tree.heading(c, text=label)
            self.tree.column(c, width=w, anchor=anchor)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self.voir_details())

        # Boutons d'actions
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(14, 0))
        actions = [
            ("+ Étudiant", self.ajouter_etudiant, SUCCESS),
            ("Détails", self.voir_details, INFO),
            ("+ Note", self.ajouter_note, PRIMARY),
            ("− Note", self.supprimer_note, (WARNING, OUTLINE)),
            ("Supprimer étudiant", self.supprimer_etudiant, (DANGER, OUTLINE)),
        ]
        for i, (txt, cmd, style) in enumerate(actions):
            ttk.Button(btns, text=txt, bootstyle=style, command=cmd).grid(
                row=0, column=i, padx=4, sticky="ew", ipady=2)
        for c in range(len(actions)):
            btns.columnconfigure(c, weight=1)

        files = ttk.Frame(self)
        files.pack(fill="x", pady=(8, 0))
        for i, (txt, cmd) in enumerate([
            ("Export CSV", self.export_csv),
            ("Import CSV", self.import_csv),
            ("Export Excel", self.export_excel),
            ("Import Excel", self.import_excel),
        ]):
            ttk.Button(files, text=txt, bootstyle=(SECONDARY, OUTLINE), command=cmd).grid(
                row=0, column=i, padx=4, sticky="ew")
        for c in range(4):
            files.columnconfigure(c, weight=1)

        self.refresh()

    def _make_card(self, parent, label, value, style, col):
        frame = ttk.Frame(parent, bootstyle=style, padding=14)
        frame.grid(row=0, column=col, sticky="ew", padx=4)
        ttk.Label(frame, text=label, bootstyle=f"inverse-{style}",
                  font=("Segoe UI", 9)).pack(anchor="w")
        val = ttk.Label(frame, text=value, bootstyle=f"inverse-{style}",
                        font=("Segoe UI", 16, "bold"))
        val.pack(anchor="w", pady=(2, 0))
        return val

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for e in self.promo.etudiants:
            self.tree.insert("", "end", values=(e.nom, e.prenom, e.age,
                                                f"{e.calculer_moyenne():.2f}"))
        self.card_nb.config(text=str(len(self.promo.etudiants)))
        self.card_moy.config(text=f"{self.promo.moyenne_generale():.2f} / 20")
        top = self.promo.meilleur_etudiant()
        self.card_top.config(text=f"{top.nom} {top.prenom}" if top else "—")

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            Messagebox.show_info("Sélectionne d'abord un étudiant.", parent=self)
            return None
        nom, prenom = self.tree.item(sel[0], "values")[:2]
        return self.promo.rechercher_etudiant(nom, prenom)

    def ajouter_etudiant(self):
        dlg = EtudiantDialog(self.winfo_toplevel())
        if not dlg.result:
            return
        d = dlg.result
        e = Etudiant(d["nom"], d["prenom"], d["age"], self.promo.filiere, self.promo.niveau)
        self.promo.ajouter_etudiant(e)
        self.refresh()

    def supprimer_etudiant(self):
        e = self._selected()
        if e and std_messagebox.askyesno(
            "Confirmation",
            f"Supprimer {e.nom} {e.prenom} ?",
            parent=self.winfo_toplevel(),
        ):
            self.promo.supprimer_etudiant(e.nom, e.prenom)
            self.refresh()

    def ajouter_note(self):
        e = self._selected()
        if not e:
            return
        dlg = NoteDialog(self.winfo_toplevel(), titre=f"Note — {e.nom} {e.prenom}")
        if dlg.result:
            e.ajouter_note(dlg.result)
            self.refresh()

    def supprimer_note(self):
        e = self._selected()
        if not e:
            return
        if not e.notes:
            Messagebox.show_info("Cet étudiant n'a aucune note.", parent=self)
            return
        matieres = [n.matiere for n in e.notes]
        m = Querybox.get_string(prompt=f"Matière à supprimer parmi : {', '.join(matieres)}",
                                title="Supprimer note", parent=self)
        if m:
            e.supprimer_note(m.strip())
            self.refresh()

    def voir_details(self):
        e = self._selected()
        if not e:
            return
        win = ttk.Toplevel(self)
        win.title(f"{e.nom} {e.prenom}")
        win.geometry("420x420")
        wrap = ttk.Frame(win, padding=20)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text=f"{e.nom} {e.prenom}",
                  font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(wrap, text=f"{e.filiere} · {e.niveau} · {e.age} ans",
                  bootstyle="secondary").pack(anchor="w", pady=(0, 8))
        ttk.Label(wrap, text=f"Moyenne : {e.calculer_moyenne():.2f} / 20",
                  font=("Segoe UI", 12, "bold"), bootstyle=SUCCESS).pack(anchor="w")
        ttk.Separator(wrap).pack(fill="x", pady=10)
        if e.notes:
            for n in e.notes:
                row = ttk.Frame(wrap)
                row.pack(fill="x", pady=2)
                ttk.Label(row, text=n.matiere).pack(side="left")
                ttk.Label(row, text=f"{n.valeur} / 20",
                          bootstyle="secondary").pack(side="right")
        else:
            ttk.Label(wrap, text="(aucune note)", bootstyle="secondary").pack(pady=10)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            try:
                self.fichiers.exporter_csv(self.promo.etudiants, path)
                Messagebox.show_info(f"CSV exporté :\n{path}", parent=self)
            except Exception as ex:
                Messagebox.show_error(str(ex), parent=self)

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            try:
                for e in self.fichiers.importer_csv(path):
                    e.filiere = self.promo.filiere
                    e.niveau = self.promo.niveau
                    self.promo.ajouter_etudiant(e)
                self.refresh()
            except Exception as ex:
                Messagebox.show_error(str(ex), parent=self)

    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            try:
                self.fichiers.exporter_excel(self.promo.etudiants, path)
                Messagebox.show_info(f"Excel exporté :\n{path}", parent=self)
            except ImportError:
                Messagebox.show_error("pandas et openpyxl requis :\npip install pandas openpyxl",
                                      parent=self)
            except Exception as ex:
                Messagebox.show_error(str(ex), parent=self)

    def import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            try:
                for e in self.fichiers.importer_excel(path):
                    e.filiere = self.promo.filiere
                    e.niveau = self.promo.niveau
                    self.promo.ajouter_etudiant(e)
                self.refresh()
            except ImportError:
                Messagebox.show_error("pandas et openpyxl requis :\npip install pandas openpyxl",
                                      parent=self)
            except Exception as ex:
                Messagebox.show_error(str(ex), parent=self)


# ────────────────── APP PRINCIPALE ──────────────────

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename=THEME_LIGHT)
        self.title("Gestion des étudiants")
        self.geometry("980x680")
        self.dark = False
        self.etab = Etablissement()
        self.fichiers = GestionFichier()

        # Barre supérieure (toggle thème) — masquée tant que non connecté
        self.bar = ttk.Frame(self, padding=(16, 10, 16, 0))
        self.btn_theme = ttk.Button(self.bar, text="🌙  Mode sombre",
                                    bootstyle=(SECONDARY, OUTLINE),
                                    command=self.toggle_theme)
        self.btn_theme.pack(side="right")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_login()

    def _swap(self, frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.bar.pack_forget()
        self._swap(LoginFrame(self.container, on_success=self.show_home))

    def show_home(self):
        self.bar.pack(fill="x", before=self.container)
        self._swap(HomeFrame(self.container, self.etab, on_open=self.show_promo))

    def show_promo(self, promo):
        self._swap(PromotionFrame(self.container, promo, self.fichiers, on_back=self.show_home))

    def toggle_theme(self):
        self.dark = not self.dark
        self.style.theme_use(THEME_DARK if self.dark else THEME_LIGHT)
        self.btn_theme.config(text="☀  Mode clair" if self.dark else "🌙  Mode sombre")


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
