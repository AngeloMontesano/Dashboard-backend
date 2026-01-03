<script setup lang="ts">
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Stammdaten</p>
        <h2 class="section-title">Artikelverwaltung</h2>
        <p class="section-subtitle">Pflege Artikel, Barcodes und Mindestbestände zentral.</p>
      </div>
      <div class="actions">
        <button class="button button--ghost" type="button">Import</button>
        <button class="button button--primary" type="button">Neuer Artikel</button>
      </div>
    </header>
    <div class="cards-grid" style="margin-bottom: 16px">
      <article class="card">
        <h3 class="card__title">Aktive Artikel</h3>
        <p class="card__value">1.284</p>
        <p class="card__hint">inkl. Varianten</p>
      </article>
      <article class="card">
        <h3 class="card__title">Mindestbestand unterschritten</h3>
        <p class="card__value">27</p>
        <p class="card__hint">braucht Nachschub</p>
      </article>
      <article class="card">
        <h3 class="card__title">Neue Barcodes</h3>
        <p class="card__value">14</p>
        <p class="card__hint">diese Woche hinzugefügt</p>
      </article>
    </div>
    <div class="placeholder">
      <p>Liste deiner Artikel erscheint hier. Filter, Suche und Export folgen.</p>
    </div>
    <table class="table">
      <thead>
        <tr>
          <th>Artikelnummer</th>
          <th>Barcode</th>
          <th>Bestand</th>
          <th>Mindestbestand</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>ART-1001</td>
          <td>4001234567890</td>
          <td>124</td>
          <td>50</td>
        </tr>
        <tr>
          <td>ART-1002</td>
          <td>4001234567891</td>
          <td>42</td>
          <td>60</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
