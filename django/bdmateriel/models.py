# coding=utf-8

from django.db import models
from django.db.models import Q

# Create your models here.
class Classification(models.Model) :
    code_classification = models.CharField(max_length=5)

    def __unicode__(self):
        return self.code_classification

class Geologie(models.Model) :
    nom = models.CharField(max_length=50)
    description = models.TextField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Géologie"
        verbose_name_plural = u"I. Géologies"

    def __unicode__(self):
        return self.nom

class CategorieBati(models.Model) :
    nom = models.CharField(max_length=50)

    def __unicode__(self):
        return self.nom

class SuperCategorieEquip(models.Model) :
    nom = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Super catégorie d'équipement"
        verbose_name_plural = u"K. Supers catégories d'équipement"

    def __unicode__(self):
        return self.nom

class CategorieEquip(models.Model) :
    nom = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Catégorie d'équipement"
        verbose_name_plural = u"L. Catégories d'équipement"

    def __unicode__(self):
        return self.nom

class CategorieInterv(models.Model) :
    nom = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nom

class Reseau(models.Model) :
    code_reseau = models.CharField(max_length=5)
    nom_reseau = models.CharField(max_length=50, null=True, blank=True)
    code_reseau_principal = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        verbose_name = "Réseau"
        verbose_name_plural = u"J. Réseaux"

    def __unicode__(self):
        return self.code_reseau

class EvenementStation(models.Model) :
    description = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Evénement de la station"
        verbose_name_plural = "Evénements des stations"

    def __unicode__(self):
        return self.description

class EvenementEquip(models.Model) :
    description = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Evénement d'un équipement"
        verbose_name_plural = "Evénements des équipements"

    def __unicode__(self):
        return self.description

class Intervenant(models.Model) :
    categorie = models.ForeignKey(CategorieInterv)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    filiale = models.CharField(max_length=50, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    portable = models.CharField(max_length=15, null=True, blank=True)
    fax = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    lien_site = models.URLField(null=True, blank=True, verify_exists=False)
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Intervenant"
        verbose_name_plural = "C. Intervenants"

    def __unicode__(self):
        return u'%s : %s' % (self.categorie.nom, self.nom)

class Adresse(models.Model) :
    intervenant = models.ForeignKey(Intervenant)
    adresse = models.CharField(max_length=100)
    commune = models.CharField(max_length=100)
    pays = models.CharField(max_length=50, null=True, blank=True)
    code_postal = models.CharField(max_length=15, null=True, blank=True)

    def __unicode__(self):
      return u'%s %s' % (self.adresse, self.commune)


class StationSite(models.Model) :
    code_station = models.CharField(max_length=25)
    nom_station = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    elevation = models.FloatField(null=True, blank=True)
    classification = models.ForeignKey(Classification, null=True, blank=True)
    photo = models.ImageField(upload_to='photos', null=True, blank=True)
    nom_site = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    commune = models.CharField(max_length=100, null=True, blank=True)
    pays =  models.CharField(max_length=50, null=True, blank=True)
    code_postal = models.CharField(max_length=15, null=True, blank=True)
    geologie = models.ForeignKey(Geologie, null=True, blank=True)
    googlemap = models.URLField(null=True, blank=True, verify_exists=False)
    lien_documentation = models.URLField(null=True, blank=True, verify_exists=False)
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Station"
        verbose_name_plural = "A. Stations"
        unique_together = ('code_station','nom_site')

    def __unicode__(self):
        return self.code_station

class StationSiteIntervenant(models.Model) :
    station = models.ForeignKey(StationSite)
    intervenant = models.ForeignKey(Intervenant,limit_choices_to = Q(categorie__nom__startswith='Pro') | Q(categorie__nom__startswith='Contact') | Q(categorie__nom__startswith='Exploitant'))
    date_debut = models.DateField()
    date_fin = models.DateField(null=True,blank=True)

    class Meta:
        verbose_name = "Intervenant de la station"
        verbose_name_plural = "G. Intervenants des stations"
        ordering = ['date_debut']

    def __unicode__(self):
        return u'%s %s' % (self.station, self.intervenant)

class Bati(models.Model) :
    station = models.ForeignKey(StationSite)
    description = models.CharField(max_length=50,unique=True)
    categorie = models.ForeignKey(CategorieBati)
    lien_documentation = models.URLField(null=True, blank=True, verify_exists=False)

    class Meta:
        verbose_name = "Bati"
        verbose_name_plural = "D. Batis"

    def __unicode__(self):
        return u'%s : %s' % (self.station, self.description)

class Equipement(models.Model) :
    super_categorie = models.ForeignKey(SuperCategorieEquip, max_length=20)
    categorie = models.ForeignKey(CategorieEquip)
    photo = models.ImageField(upload_to='photos', null=True, blank=True)
    constructeur = models.ForeignKey(Intervenant, related_name = "constructeur", limit_choices_to = {'categorie__nom__in' : ['Constructeur']})
    fournisseur = models.ForeignKey(Intervenant, related_name = "fournisseur", limit_choices_to = {'categorie__nom__in' : ['Fournisseur']}, null=True, blank=True)
    modele = models.CharField(max_length=50)
    no_serie = models.CharField(max_length=50)
    dimension = models.CharField(max_length=20, null=True, blank=True)
    poids = models.CharField(max_length=5, null=True, blank=True)
    lien_documentation = models.URLField(null=True, blank=True,verify_exists=False)
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Equipement"
        verbose_name_plural = "B. Equipements"
        ordering = ['super_categorie']
        unique_together = ('constructeur','modele','no_serie')

    def __unicode__(self):
        return u'%s : %s' % (self.modele, self.no_serie)

class EquipIntervenant(models.Model) :
    equipement = models.ForeignKey(Equipement)
    intervenant = models.ForeignKey(Intervenant)#,limit_choices_to = {'categorie__nom__in' : ['Proprietaire','Exploitant']})
    date_debut = models.DateField()
    date_fin = models.DateField(null=True,blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Intervenant de l'équipement"
        verbose_name_plural = u"H. Intervenants des équipements"
        ordering = ['date_debut']

    def __unicode__(self):
        return u'%s %s %s' % (self.equipement, self.intervenant.categorie, self.intervenant.nom)

class EquipStationSite(models.Model) :
    equipement = models.ForeignKey(Equipement)
    station = models.ForeignKey(StationSite)
    reseau = models.ForeignKey(Reseau,null=True,blank=True)
    bati = models.ForeignKey(Bati, null=True,blank=True)
    equipement_hote = models.ForeignKey(Equipement, related_name="equipement_hote", null=True,blank=True)
    detail = models.TextField(null=True,blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True,blank=True)

    class Meta:
        verbose_name = "Emplacement de l'équipement"
        verbose_name_plural = "Emplacements des équipements"
        ordering = ['date_debut']

    def __unicode__(self):
        return u'%s %s' % (self.equipement, self.station)

class HistoriqueStationSite(models.Model) :
    station = models.ForeignKey(StationSite)
    evenement = models.ForeignKey(EvenementStation)
    etat = models.CharField(max_length=20,null=True,blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True,blank=True)
    note = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = "Historique de la station"
        verbose_name_plural = "E. Historique des stations"
        ordering = ['date_debut']

    def __unicode__(self):
        return self.evenement.description

class HistoriqueEquip(models.Model) :
    equipement = models.ForeignKey(Equipement)
    evenement = models.ForeignKey(EvenementEquip)
    etat = models.CharField(max_length=20,null=True,blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True,blank=True)
    note = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = "Historique de l'équipement"
        verbose_name_plural = u"F. Historique des équipements"
        ordering = ['date_debut']

    def __unicode__(self):
        return self.evenement.description


