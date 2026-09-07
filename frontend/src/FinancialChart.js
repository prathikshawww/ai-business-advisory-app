import React, { useState, useEffect } from "react";
import { Line, Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import jsPDF from "jspdf";
import "jspdf-autotable";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function FinancialChart({ projectData }) {
  const [quarterlyData, setQuarterlyData] = useState([]);
  const [chartType, setChartType] = useState("bar");

  // 🔽 Fetch quarterly financials
  useEffect(() => {
    fetch("http://localhost:5000/api/financials")
      .then((res) => res.json())
      .then((json) => setQuarterlyData(json));
  }, []);

  // 🔽 Export CSV
  const exportCSV = () => {
    if (!quarterlyData.length) return;
    const headers = ["Quarter", "Revenue", "Expenses", "Profit", "Margin (%)", "Growth Rate (%)"];
    const rows = quarterlyData.map(item => [
      item.quarter,
      item.revenue,
      item.expenses,
      item.profit,
      item.margin,
      item.growth_rate
    ]);

    let csvContent = "data:text/csv;charset=utf-8,"
      + headers.join(",") + "\n"
      + rows.map(e => e.join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.href = encodedUri;
    link.download = "financial_data.csv";
    link.click();
  };

  // 🔽 Export PDF
  const exportPDF = () => {
    const doc = new jsPDF();
    doc.text("Financial Report", 14, 15);

    if (quarterlyData.length) {
      const headers = [["Quarter", "Revenue", "Expenses", "Profit", "Margin (%)", "Growth Rate (%)"]];
      const rows = quarterlyData.map(item => [
        item.quarter,
        item.revenue,
        item.expenses,
        item.profit,
        item.margin,
        item.growth_rate
      ]);
      doc.autoTable({ head: headers, body: rows, startY: 25 });
    }

    if (projectData && typeof projectData === "object") {
      const projHeaders = [["Metric", "Value"]];
      const projRows = Object.entries(projectData);
      doc.autoTable({ head: projHeaders, body: projRows, startY: doc.lastAutoTable.finalY + 10 });
    }

    doc.save("financial_report.pdf");
  };

  // 🔽 Quarterly chart (Line + Bar overlay)
  const quarterlyChartData = {
    labels: quarterlyData.map((item) => item.quarter),
    datasets: [
      {
        label: "Revenue",
        data: quarterlyData.map((item) => item.revenue),
        borderColor: "green",
        backgroundColor: "rgba(0, 128, 0, 0.2)",
        tension: 0.3,
      },
      {
        label: "Expenses",
        data: quarterlyData.map((item) => item.expenses),
        borderColor: "red",
        backgroundColor: "rgba(255, 0, 0, 0.2)",
        tension: 0.3,
      },
      {
        label: "Profit",
        data: quarterlyData.map((item) => item.profit),
        borderColor: "blue",
        backgroundColor: "rgba(0, 0, 255, 0.2)",
        tension: 0.3,
      },
      {
        type: "bar",
        label: "Growth Rate (%)",
        data: quarterlyData.map((item) => item.growth_rate),
        backgroundColor: "rgba(255, 165, 0, 0.6)",
        yAxisID: "y1",
      },
      {
        label: "Margin (%)",
        data: quarterlyData.map((item) => item.margin),
        borderColor: "purple",
        backgroundColor: "rgba(128, 0, 128, 0.2)",
        tension: 0.3,
        yAxisID: "y1",
      },
    ],
  };

  const quarterlyOptions = {
    responsive: true,
    interaction: { mode: "index", intersect: false },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: "Quarterly Financial Dashboard",
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const datasetLabel = context.dataset.label || "";
            const value = context.raw;
            if (datasetLabel.includes("Margin") || datasetLabel.includes("Growth")) {
              return `${datasetLabel}: ${value}%`;
            }
            return `${datasetLabel}: ₹${value}`;
          },
        },
      },
    },
    scales: {
      y: { type: "linear", position: "left", title: { display: true, text: "Amount (₹)" } },
      y1: { type: "linear", position: "right", title: { display: true, text: "Percentage (%)" }, grid: { drawOnChartArea: false } },
    },
  };

  // 🔽 Project metrics chart (Bar/Pie toggle)
  const projectLabels = projectData ? Object.keys(projectData) : [];
  const projectValues = projectData ? Object.values(projectData).map(val =>
    typeof val === "string" && val.includes("%") ? parseFloat(val) : parseFloat(val) || 0
  ) : [];

  const projectChartData = {
    labels: projectLabels,
    datasets: [
      {
        label: "Project Metrics",
        data: projectValues,
        backgroundColor: ["#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#f1c40f"],
      },
    ],
  };

  return (
    <div>
      {/* Quarterly chart */}
      {quarterlyData.length > 0 && (
        <Line data={quarterlyChartData} options={quarterlyOptions} />
      )}

      {/* Project metrics chart */}
      {projectData && (
        <div style={{ marginTop: "30px" }}>
          <button
            onClick={() => setChartType(chartType === "bar" ? "pie" : "bar")}
            style={{
              marginBottom: "10px",
              padding: "8px 12px",
              backgroundColor: "#34495e",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Switch to {chartType === "bar" ? "Pie" : "Bar"} Chart
          </button>

          {chartType === "bar" ? (
            <Bar data={projectChartData} />
          ) : (
            <Pie data={projectChartData} />
          )}
        </div>
      )}

      {/* Export buttons */}
      <div style={{ marginTop: "20px" }}>
        <button
          onClick={exportCSV}
          style={{
            marginRight: "10px",
            padding: "10px 15px",
            backgroundColor: "darkblue",color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          ⬇ Download CSV
        </button>
        <button
          onClick={exportPDF}
          style={{
            padding: "10px 15px",
            backgroundColor: "darkred",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          📄 Download PDF
        </button>
      </div>
    </div>
  );
}

export default FinancialChart;