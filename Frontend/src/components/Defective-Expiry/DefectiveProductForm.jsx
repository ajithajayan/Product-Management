import React, { useState } from 'react';
import axios from 'axios';
import AsyncSelect from 'react-select/async';
import Swal from 'sweetalert2';
import { baseUrl } from "../../utils/constants/Constants";

const DefectiveProductForm = () => {
  const [productDetails, setProductDetails] = useState({
    id: null,
    qty_defective: 0,
    remarks: "",
    productCode: "",
    brandName: "",
    categoryName: "",
    supplierName: "",
    manufacturingDate: "",
    expiryDate: "",
    availableQuantity: 0,
  });

  const loadProductOptions = async (inputValue) => {
    const response = await axios.get(`${baseUrl}store/products/?search=${inputValue}`);
    return response.data.results.map((product) => ({
      label: `${product.product_code} - ${product.name}`,
      value: product.id,
    }));
  };

  const handleProductChange = async (selectedOption) => {
    if (selectedOption) {
      const response = await axios.get(`${baseUrl}store/inventory/?search=${selectedOption.label}`);
      const product = response.data.results[0];

      setProductDetails({
        ...productDetails,
        id: selectedOption.value,
        productCode: product.product_code,
        brandName: product.brand_name,
        categoryName: product.category_name,
        supplierName: product.supplier_name,
        manufacturingDate: product.manufacturing_date,
        expiryDate: product.expiry_date,
        availableQuantity: product.remaining_quantity,
      });
    }
  };

  const handleSubmitDefective = async () => {
    if (!productDetails.id) {
      Swal.fire("Error", "Product must be selected before removing defective quantity", "error");
      return;
    }

    try {
      await axios.post(`${baseUrl}store/remove-defective-product/`, {
        product_id: productDetails.id,
        qty_to_remove: productDetails.qty_defective,
        remarks: productDetails.remarks
      });
      Swal.fire("Success", "Defective product removed successfully", "success");
      setProductDetails({
        id: null,
        qty_defective: 0,
        remarks: "",
        productCode: "",
        brandName: "",
        categoryName: "",
        supplierName: "",
        manufacturingDate: "",
        expiryDate: "",
        availableQuantity: 0,
      });
    } catch (error) {
      console.error("Error removing defective product:", error);
      Swal.fire("Error", "Failed to remove defective product", "error");
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Remove Defective Product</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-3">
          <label className="block text-sm font-medium text-gray-700">Product</label>
          <AsyncSelect
            loadOptions={loadProductOptions}
            onChange={handleProductChange}
            placeholder="Search Product Code or Name"
            className="mt-1"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Available Quantity</label>
          <input
            type="number"
            value={productDetails.availableQuantity}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Brand</label>
          <input
            type="text"
            value={productDetails.brandName}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <input
            type="text"
            value={productDetails.categoryName}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Supplier</label>
          <input
            type="text"
            value={productDetails.supplierName}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Manufacturing Date</label>
          <input
            type="date"
            value={productDetails.manufacturingDate}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
          <input
            type="date"
            value={productDetails.expiryDate}
            readOnly
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Quantity to Remove</label>
          <input
            type="number"
            value={productDetails.qty_defective}
            onChange={(e) => setProductDetails({ ...productDetails, qty_defective: parseInt(e.target.value) })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <div className="col-span-3">
          <label className="block text-sm font-medium text-gray-700">Remarks</label>
          <input
            type="text"
            value={productDetails.remarks}
            onChange={(e) => setProductDetails({ ...productDetails, remarks: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </div>
      <div className="mt-6 flex justify-end space-x-4">
        <button
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          onClick={() => setProductDetails({ id: null, qty_defective: 0, remarks: "" })}
        >
          Cancel
        </button>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={handleSubmitDefective}
        >
          Remove Defective Product
        </button>
      </div>
    </div>
  );
};

export default DefectiveProductForm;
