import React, { useState, useEffect } from "react";
import axios from "axios";
import AsyncSelect from "react-select/async";
import Swal from "sweetalert2";
import { baseUrl } from "../../utils/constants/Constants";
import ProductOutModal from "./ProductOutModal";

const TransactionOutForm = () => {
  const [transactionDetails, setTransactionDetails] = useState({
    date: "",
    branch: null,
    transferInvoiceNumber: "",
    branchInCharge: "",
    products: [],
    remarks: "",
  });

  const [showModal, setShowModal] = useState(false);
  const [totalQuantity, setTotalQuantity] = useState(0);

  useEffect(() => {
    calculateTotalQuantity();
  }, [transactionDetails.products]);

  const handleBranchChange = (selectedOption) => {
    setTransactionDetails({ ...transactionDetails, branch: selectedOption });
  };

  const loadBranchOptions = async (inputValue) => {
    const response = await axios.get(`${baseUrl}store/branches/?search=${inputValue}`);
    return response.data.results.map((branch) => ({
      label: branch.name,
      value: branch.branch_code,
    }));
  };

  const handleInputChange = (newValue) => {
    return newValue.replace(/\W/g, '');
  };

  const handleAddProduct = (product) => {
    setTransactionDetails({
      ...transactionDetails,
      products: [...transactionDetails.products, product],
    });
    setShowModal(false);
  };

  const calculateTotalQuantity = () => {
    const total = transactionDetails.products.reduce((sum, product) => sum + product.qty_requested, 0);
    setTotalQuantity(total);
  };

  const handleClearProducts = () => {
    setTransactionDetails({ ...transactionDetails, products: [] });
    setTotalQuantity(0);
  };

  const handleSubmit = async () => {
    const transformedData = {
        date: transactionDetails.date,
        branch: transactionDetails.branch?.value || null,
        transfer_invoice_number: transactionDetails.transferInvoiceNumber,
        branch_in_charge: transactionDetails.branchInCharge,
        transaction_details: transactionDetails.products.map((product) => ({
            product: product.id, // Ensure this is the product ID (pk)
            qty_requested: product.qty_requested,
        })),
        remarks: transactionDetails.remarks,
    };

    try {
        await axios.post(`${baseUrl}store/product-out-transactions/`, transformedData);
        Swal.fire("Success", "Transaction saved successfully", "success");
        handleClearProducts(); // Clear form after submission
    } catch (error) {
        console.error("Error saving transaction:", error);
        Swal.fire("Error", "Failed to save the transaction", "error");
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Date</label>
          <input
            type="date"
            value={transactionDetails.date}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, date: e.target.value })}
            placeholder="Select Date"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Select Branch</label>
          <AsyncSelect
            cacheOptions
            loadOptions={loadBranchOptions}
            onInputChange={handleInputChange}
            onChange={handleBranchChange}
            isClearable
            placeholder="Search Branch"
            className="mt-1 block w-full"
            defaultOptions
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Transfer Invoice Number</label>
          <input
            type="text"
            value={transactionDetails.transferInvoiceNumber}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, transferInvoiceNumber: e.target.value })}
            placeholder="Enter Transfer Invoice Number"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Branch In Charge</label>
          <input
            type="text"
            value={transactionDetails.branchInCharge}
            onChange={(e) => setTransactionDetails({ ...transactionDetails, branchInCharge: e.target.value })}
            placeholder="Enter Branch In Charge"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="mt-6">
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={() => setShowModal(true)}
        >
          Add Product
        </button>
      </div>

      <div className="mt-6">
        {transactionDetails.products.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded">
              <thead className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                <tr>
                  <th className="py-3 px-6 text-left">#</th>
                  <th className="py-3 px-6 text-left">Product Code</th>
                  <th className="py-3 px-6 text-left">Name</th>
                  <th className="py-3 px-6 text-left">Brand</th>
                  <th className="py-3 px-6 text-left">Category</th>
                  <th className="py-3 px-6 text-left">Barcode</th>
                  <th className="py-3 px-6 text-left">Manufacturing Date</th>
                  <th className="py-3 px-6 text-left">Expiry Date</th>
                  <th className="py-3 px-6 text-left">Available Quantity</th>
                  <th className="py-3 px-6 text-left">Requested Quantity</th>
                </tr>
              </thead>
              <tbody className="text-gray-600 text-sm">
                {transactionDetails.products.map((product, index) => (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-100">
                    <td className="py-3 px-6 text-left">{index + 1}</td>
                    <td className="py-3 px-6 text-left">{product.productCode}</td>
                    <td className="py-3 px-6 text-left">{product.name}</td>
                    <td className="py-3 px-6 text-left">{product.brandName}</td>
                    <td className="py-3 px-6 text-left">{product.categoryName}</td>
                    <td className="py-3 px-6 text-left">{product.barcode}</td>
                    <td className="py-3 px-6 text-left">{product.manufacturingDate}</td>
                    <td className="py-3 px-6 text-left">{product.expiryDate}</td>
                    <td className="py-3 px-6 text-left">{product.availableQuantity}</td>
                    <td className="py-3 px-6 text-left">{product.qty_requested}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No products added. Click "Add Product" to start.
          </div>
        )}

        {/* Total Quantity */}
        <div className="mt-4 bg-gray-200 p-4 rounded text-right">
          <strong>Total Quantity:</strong> {totalQuantity}
        </div>
      </div>

      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700">Remarks</label>
        <textarea
          value={transactionDetails.remarks}
          onChange={(e) => setTransactionDetails({ ...transactionDetails, remarks: e.target.value })}
          placeholder="Enter any remarks..."
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div className="mt-6 flex space-x-4">
        <button
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          onClick={handleSubmit}
        >
          Save and Print
        </button>
        <button
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          onClick={handleClearProducts}
        >
          Clear
        </button>
      </div>

      {/* Product Modal */}
      {showModal && (
        <ProductOutModal
          setShowModal={setShowModal}
          addProduct={handleAddProduct}
        />
      )}
    </div>
  );
};

export default TransactionOutForm;
