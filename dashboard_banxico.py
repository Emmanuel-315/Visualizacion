with izquierda:
    if len(claves) == 1:
        st.subheader("La serie y su tendencia")
        principal["Suave"] = principal["Valor"].rolling(suavizado).mean()

        fig, ax = plt.subplots(figsize=(6, 3.4))
        ax.plot(principal["Fecha"], principal["Valor"], color=GRIS,
                linewidth=0.9, label="Valor diario")
        ax.plot(principal["Fecha"], principal["Suave"], color=AZUL,
                linewidth=2, label=f"Media móvil {suavizado} días")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Valor de la serie")
        ax.legend(frameon=False)
        st.pyplot(fig)
    else:
        # Varias series van en escalas distintas: se normalizan a base 100
        # para que lo comparable sea el crecimiento, no el nivel.
        st.subheader("Comparación en base 100")
        limpio = limpio.sort_values("Fecha")
        limpio["Base100"] = (limpio.groupby("Clave")["Valor"]
                                   .transform(lambda s: s / s.iloc[0] * 100))

        fig, ax = plt.subplots(figsize=(6, 3.4))
        for i, clave in enumerate(claves):
            parte = limpio[limpio["Clave"] == clave]
            if parte.empty:
                continue
            ax.plot(parte["Fecha"], parte["Base100"],
                    color=CUALI[i % len(CUALI)], linewidth=1.8, label=clave)
        ax.axhline(100, color="gray", linewidth=0.8)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Índice base 100")
        ax.legend(frameon=False)
        st.pyplot(fig)

with derecha:
    st.subheader("Cambio de un mes a otro")
    # Para un precio, el valor del mes es el de cierre, no el promedio.
    mensual = (principal.set_index("Fecha")["Valor"].resample("ME").last())
    cambio = (mensual.pct_change() * 100).dropna()

    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.bar(cambio.index,
           cambio.values,
           color=[ROJO if v > 0 else AZUL_POS for v in cambio.values],
           width=20)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cambio respecto al mes anterior (%)")
    st.pyplot(fig)
    st.caption("Rojo: el valor subió. Azul: bajó. Para un tipo de cambio, "
               "subir significa que el peso se debilitó.")

abajo_izq, abajo_der = st.columns(2)
with abajo_izq:
    st.subheader("Qué tan movido estuvo cada año")
    principal["Variacion"] = principal["Valor"].pct_change() * 100
    porAnio = principal.dropna(subset=["Variacion"])

    fig, ax = plt.subplots(figsize=(6, 3.4))
    sns.boxplot(data=porAnio, x="Anio", y="Variacion", color=GRIS, ax=ax)
    ax.axhline(0, color=ROJO, linewidth=1, linestyle="--")
    ax.set_xlabel("Año")
    ax.set_ylabel("Variación diaria (%)")
    st.pyplot(fig)

with abajo_der:
    st.subheader("Promedio por mes y año")
    calor = principal.pivot_table(index="Anio", columns="Mes",
                                  values="Valor", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(6, 3.4))
    imagen = ax.imshow(calor, cmap="YlGnBu", aspect="auto")
    fig.colorbar(imagen, ax=ax)
    ax.set_xticks(range(len(calor.columns)))
    ax.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul",
                        "Ago", "Sep", "Oct", "Nov", "Dic"][:len(calor.columns)])
    ax.set_yticks(range(len(calor.index)))
    ax.set_yticklabels(calor.index)
    ax.grid(False)
    st.pyplot(fig)
    st.caption("Escala secuencial: el valor tiene orden pero no un cero "
               "con significado, así que no va divergente.")


# ─── Gráfica adicional: rango de valores máximos y mínimos por mes ───
st.divider()
st.subheader("Rango de valores máximos y mínimos por mes")

# Agrupamos los valores diarios de la serie principal por mes
datos_mensuales = principal.set_index("Fecha")["Valor"].resample("ME")

# Calculamos el valor mínimo y máximo alcanzado durante cada mes
rango_mensual = datos_mensuales.agg(["min", "max"]).dropna()

# Creamos la figura de la gráfica
fig, ax = plt.subplots(figsize=(12, 4.5))

# Dibujamos la línea del máximo mensual
ax.plot(rango_mensual.index, rango_mensual["max"],
        color=ROJO, linewidth=1.8, label="Máximo mensual")

# Dibujamos la línea del mínimo mensual
ax.plot(rango_mensual.index, rango_mensual["min"],
        color=AZUL_POS, linewidth=1.8, label="Mínimo mensual")

# Sombreamos el espacio entre las líneas para mostrar el rango mensual
ax.fill_between(rango_mensual.index, rango_mensual["min"],
               rango_mensual["max"], color=GRIS, alpha=0.4,
               label="Rango mensual")

# Agregamos etiquetas y leyenda
ax.set_xlabel("Mes")
ax.set_ylabel("Valor de la serie")
ax.legend(frameon=False)
st.pyplot(fig)

# ─── Datos ─────────────────────────────────────────────────────────────
with st.expander("Ver y descargar los datos"):
    st.write("Días marcados como N/E por serie:", faltantes)
    st.dataframe(df)
    st.download_button(
        "Descargar CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"sie_{'_'.join(claves)}_{inicio}_{fin}.csv",
        mime="text/csv",
    )
