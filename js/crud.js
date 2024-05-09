document.addEventListener("DOMContentLoaded", () => {
    const idToken = sessionStorage.getItem("idToken");
    const Url = "https://gk8v06fere.execute-api.us-east-1.amazonaws.com/dev/crud/read";
    const Update_url = "https://gk8v06fere.execute-api.us-east-1.amazonaws.com/dev/crud/update";
    const Delete_url = "https://gk8v06fere.execute-api.us-east-1.amazonaws.com/dev/crud/delete";
    const Insert_url = "https://gk8v06fere.execute-api.us-east-1.amazonaws.com/dev/crud/insert";

    // Function to create a new row
    function createRow(category, amount, timestamp, isadded) {
        // Create table row
        const row = document.createElement("tr");

        // Create table data for category
        const categoryCell = document.createElement("td");
        // Create select element for category
        const categorySelect = document.createElement("select");

        // Options for food, clothing, and living
        const categoryOptions = ["Food", "Clothing", "Living", "Transportation", "Others"];

        // Create option elements for each category option
        categoryOptions.forEach((option) => {
            const optionElement = document.createElement("option");
            optionElement.value = option;
            optionElement.textContent = option.charAt(0).toUpperCase() + option.slice(1);
            categorySelect.appendChild(optionElement);
        });

        // Set default value to the current category
        categorySelect.value = category;

        categoryCell.appendChild(categorySelect);
        row.appendChild(categoryCell);

        // Create table data for amount
        const amountCell = document.createElement("td");
        // Create input element for amount
        const amountInput = document.createElement("input");
        amountInput.type = "number";
        amountInput.value = amount;
        amountCell.appendChild(amountInput);
        row.appendChild(amountCell);

        // Create table data for timestamp
        const timestampCell = document.createElement("td");
        timestampCell.textContent = timestamp; // Adjust this according to your timestamp format
        row.appendChild(timestampCell);

        // Create table data for Update button
        if(!isadded)
        {
            const updateCell = document.createElement("td");
            const updateButton = document.createElement("button");
            updateButton.textContent = "Update";
            updateButton.addEventListener("click", () => {
                const newCategory = categorySelect.value;
                const newAmount = amountInput.value;

                // Check if the amount is a valid number and not negative
                if (!isNaN(newAmount) && newAmount > 0) {
                    // Send the updated values to the backend
                    axios.post(Update_url, {
                        category: category,
                        amount: amount,
                        timestamp: timestamp,
                        new_amount: newAmount,
                        new_category: newCategory
                    }, {
                        headers: {
                            Authorization: `Bearer ${idToken}`,
                        }
                    })
                    .then((response) => {
                        console.log(response.data);
                        window.location.reload();
                        // Handle successful update response if needed
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        // Handle error if needed
                    });
                } else {
                    // Display prompt for invalid amount input
                    alert("Invalid amount. Please enter a valid positive number.");
                }
            });
            updateCell.appendChild(updateButton);
            row.appendChild(updateCell);

            // Create table data for Delete button
            const deleteCell = document.createElement("td");
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.addEventListener("click", () => {
                // Add functionality for Delete button here
                axios.delete(Delete_url, {
                    headers: {
                        Authorization: `Bearer ${idToken}`,
                    },
                    params: {
                        timestamp: timestamp
                    },
                })
                .then((response) => {
                    console.log(response.data);
                    window.location.reload();
                    // Handle successful update response if needed
                })
                .catch((error) => {
                    console.error("Error:", error);
                    // Handle error if needed
                });
            });
            deleteCell.appendChild(deleteButton);
            row.appendChild(deleteCell);
        }
        else
        {
            const addCell = document.createElement("td");
            const addButton = document.createElement("button");
            addButton.textContent = "Add";
            addButton.addEventListener("click", () => {
                const newCategory = categorySelect.value;
                const newAmount = amountInput.value;
                console.log(category)
                if (newCategory != "" && !isNaN(newAmount) && newAmount > 0) {
                    axios.post(Insert_url, {
                        category: newCategory,
                        amount: newAmount,
                        timestamp: timestamp,
                    }, {
                        headers: {
                            Authorization: `Bearer ${idToken}`,
                        }
                    })
                    .then((response) => {
                        console.log(response.data);
                        window.location.reload();
                        // Handle successful update response if needed
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        // Handle error if needed
                    });
                }
                else
                {
                    alert("Invalid input");
                }
            });
            addCell.appendChild(addButton);
            row.appendChild(addCell);
        }
        // Append row to table body
        categoryTableBody.appendChild(row);
    }

    // Function to add a new row
    function addNewRow() {
        // Get current timestamp
        const timestamp = new Date();
        const formattedTimestamp = `${timestamp.getFullYear()}-${(timestamp.getMonth() + 1).toString().padStart(2, '0')}-${timestamp.getDate().toString().padStart(2, '0')} ${timestamp.getHours().toString().padStart(2, '0')}:${timestamp.getMinutes().toString().padStart(2, '0')}:${timestamp.getSeconds().toString().padStart(2, '0')}`;
        console.log(formattedTimestamp);

        // Create a new row with default values
        createRow("", "", formattedTimestamp, 1);
    }

    axios
        .get(Url, {
            headers: {
                Authorization: `Bearer ${idToken}`,
            },
        })
        .then((response) => {
            console.log(response.data);
            const data = response.data; // Assuming the response is an array of objects
            const categoryTableBody = document.getElementById("categoryTableBody");

            // Clear any existing rows in the table body
            categoryTableBody.innerHTML = "";

            // Loop through the data and populate the table
            data.forEach((item) => {
                createRow(item.category, item.amount, item.timestamp, 0);
            });

            // Add a new row at the bottom of the form
            addNewRow();
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});
