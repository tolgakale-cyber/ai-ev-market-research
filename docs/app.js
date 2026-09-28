const ctx = document.getElementById("salesChart");

async function loadMarketData() {
    try {
        const response = await fetch("iea_ev_sales.json");

        if (!response.ok) {
            throw new Error(`JSON yüklenemedi: ${response.status}`);
        }

        const marketData = await response.json();

        const labels = marketData.veriler.map(item =>
            item.tahmin ? `${item.yil} Tahmin` : String(item.yil)
        );

        const salesData = {
            labels: labels,

            datasets: [
                {
                    label: "Çin",
                    data: marketData.veriler.map(item => item.cin_milyon),
                    borderWidth: 3,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: "Avrupa",
                    data: marketData.veriler.map(item => item.avrupa_milyon),
                    borderWidth: 3,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: "ABD",
                    data: marketData.veriler.map(item => item.abd_milyon),
                    borderWidth: 3,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: "Diğer Dünya",
                    data: marketData.veriler.map(item => item.diger_dunya_milyon),
                    borderWidth: 3,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 7
                }
            ]
        };

        new Chart(ctx, {
            type: "line",
            data: salesData,

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                plugins: {
                    legend: {
                        position: "top",

                        labels: {
                            color: "#91a4b7",
                            usePointStyle: true,
                            pointStyle: "circle",
                            padding: 20
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} milyon`;
                            },

                            afterTitle: function(items) {
                                if (items[0].label === "2026 Tahmin") {
                                    return "IEA tahmini";
                                }

                                return "";
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        grid: {
                            color: "rgba(255,255,255,0.04)"
                        },

                        ticks: {
                            color: "#91a4b7"
                        },

                        border: {
                            color: "rgba(255,255,255,0.08)"
                        }
                    },

                    y: {
                        beginAtZero: true,

                        title: {
                            display: true,
                            text: "Milyon araç",
                            color: "#91a4b7"
                        },

                        grid: {
                            color: "rgba(255,255,255,0.05)"
                        },

                        ticks: {
                            color: "#91a4b7"
                        },

                        border: {
                            color: "rgba(255,255,255,0.08)"
                        }
                    }
                }
            }
        });

        console.log(
            `IEA verisi yüklendi: ${marketData.veriler.length} dönem`
        );

    } catch (error) {
        console.error("EV pazar verisi yüklenirken hata oluştu:", error);
    }
}

loadMarketData();

async function loadFinalReport() {
    const reportContainer = document.getElementById("final-report");

    if (!reportContainer) {
        return;
    }

    try {
        const response = await fetch("final_report.md");

        if (!response.ok) {
            throw new Error(`Rapor yüklenemedi: ${response.status}`);
        }

                const markdown = await response.text();

        const summaryStart = markdown.indexOf("## Yönetici Özeti");
        const summaryEnd = markdown.indexOf("## Temel Pazar Eğilimleri");

        let displayMarkdown = markdown;

        if (summaryStart !== -1 && summaryEnd !== -1) {
            displayMarkdown = markdown.slice(summaryStart, summaryEnd);
        }

        const html = displayMarkdown
            .replace(/^# (.*)$/gm, "<h2>$1</h2>")
            .replace(/^## (.*)$/gm, "<h3>$1</h3>")
            .replace(/^### (.*)$/gm, "<h4>$1</h4>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/^- (.*)$/gm, "<li>$1</li>")
            .replace(/\n{2,}/g, "</p><p>")
            .replace(/\n/g, "<br>");

        reportContainer.innerHTML = `<div class="generated-report"><p>${html}</p></div>`;

        console.log("AI final raporu siteye yüklendi.");

    } catch (error) {
        console.error("AI raporu yüklenirken hata oluştu:", error);

        reportContainer.innerHTML = `
            <p>
                Güncel AI araştırma raporu şu anda yüklenemiyor.
            </p>
        `;
    }
}

loadFinalReport();