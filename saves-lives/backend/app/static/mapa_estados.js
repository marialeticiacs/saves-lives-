function configurarEventosGeoJson(geoJsonLayer) {
    geoJsonLayer.eachLayer(function(layer) {
        layer.on('click', function(e) {
            const estado = layer.feature.properties.name; // Ajuste para a propriedade correta no seu GeoJSON

            // Faz a requisição para a rota de clima
            fetch(`/clima/estado?estado=${estado}`)
                .then(response => response.json())
                .then(data => {
                    if (data.erro) {
                        alert("Erro ao obter dados climáticos: " + data.erro);
                    } else {
                        document.getElementById("info-container").style.display = "block";
                        document.getElementById("estado-nome").textContent = `Estado: ${data.local}`;
                        document.getElementById("estado-temperatura").textContent = `Temperatura: ${data.temperatura} °C`;
                        document.getElementById("estado-clima").textContent = `Clima: ${data.clima}`;
                        document.getElementById("estado-umidade").textContent = `Umidade: ${data.umidade}%`;
                        document.getElementById("estado-vento").textContent = `Vento: ${data.vento} km/h`;
                    }
                })
                .catch(error => console.error("Erro ao obter dados do clima:", error));
        });

        layer.on('mouseover', function(e) {
            e.target.setStyle({
                weight: 3,
                color: "blue",
                fillOpacity: 0.7
            });
        });

        layer.on('mouseout', function(e) {
            geoJsonLayer.resetStyle(e.target);
        });
    });
}
