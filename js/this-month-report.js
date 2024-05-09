document.addEventListener("DOMContentLoaded", () => {
    const d = new Date()
    year = d.getFullYear()
    month = d.getMonth() + 1
    //console.log(year,month)

    const idToken = sessionStorage.getItem("idToken");
    const Url = "https://gk8v06fere.execute-api.us-east-1.amazonaws.com/dev/report/month"
    axios.get(Url, {
      headers: { 
        Authorization: `Bearer ${idToken}`,
      },
      params: {
          month: month,
          year: year
      },
    }).then(
      (response) => {
        // console.log(response);
        document.getElementById("food-amount").textContent = response.data.Food;
        document.getElementById("clothing-amount").textContent = response.data.Clothing;
        document.getElementById("living-amount").textContent = response.data.Living;
        document.getElementById("trans-amount").textContent = response.data.Transportation;
        document.getElementById("others-amount").textContent = response.data.Others;
        document.getElementById("total-amount").textContent = response.data.total;

        $("#sparkline-food").sparkline([response.data.Food, response.data.total - response.data.Food], {
          type: 'pie',
          height: '140',
          sliceColors: ['#D80027', '#ebebeb']
        });

        $("#sparkline-clothing").sparkline([response.data.Clothing, response.data.total - response.data.Clothing], {
          type: 'pie',
          height: '140',
          sliceColors: ['#65b12d', '#ebebeb']
        });

        $("#sparkline-living").sparkline([response.data.Living, response.data.total - response.data.Living], {
          type: 'pie',
          height: '140',
          sliceColors: ['#933EC5', '#ebebeb']
        });

        $("#sparkline-trans").sparkline([response.data.Transportation, response.data.total - response.data.Transportation], {
          type: 'pie',
          height: '140',
          sliceColors: ['#006DF0', '#ebebeb']
        });

        $("#sparkline-others").sparkline([response.data.Others, response.data.total - response.data.Others], {
          type: 'pie',
          height: '140',
          sliceColors: ['#680027', '#ebebeb']
        });
      }
    ).catch((error) => {
      console.error("Error:", error);
    });
  });