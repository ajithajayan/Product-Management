import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { baseUrl } from '../../utils/constants/Constants';

const ProductEditForm = ({ product, fetchProducts, setShowModal }) => {
  const [productCode, setProductCode] = useState('');
  const [name, setName] = useState('');
  const [purchaseDate, setPurchaseDate] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [expiryDate, setExpiryDate] = useState('');
  const [manufacturingDate, setManufacturingDate] = useState('');
  const [openingStock, setOpeningStock] = useState(0);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    fetchBrands();
    fetchCategories();
    fetchSuppliers();

    if (product) {
      // Prefill form fields with product data
      setProductCode(product.product_code);
      setName(product.name);
      setPurchaseDate(product.purchase_date);
      setQuantity(product.quantity);
      setExpiryDate(product.expiry_date);
      setManufacturingDate(product.manufacturing_date);
      setOpeningStock(product.opening_stock);

      // Manually trigger state updates for Select components
      setSelectedBrand({ label: product.brand_name, value: product.brand });
      setSelectedCategory({ label: product.category_name, value: product.category });
      setSelectedSupplier({ label: product.supplier_name, value: product.supplier });
    }
  }, [product]);

  const fetchBrands = async () => {
    const response = await axios.get(baseUrl + 'store/brands/');
    setBrands(response.data.results.map(brand => ({ label: brand.name, value: brand.id })));
  };

  const fetchCategories = async () => {
    const response = await axios.get(baseUrl + 'store/categories/');
    setCategories(response.data.results.map(category => ({ label: category.name, value: category.id })));
  };

  const fetchSuppliers = async () => {
    const response = await axios.get(baseUrl + 'store/suppliers/');
    setSuppliers(response.data.results.map(supplier => ({ label: supplier.name, value: supplier.id })));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Construct the product data object
    const productData = {
      product_code: productCode,
      name,
      purchase_date: purchaseDate,
      quantity,
      expiry_date: expiryDate,
      manufacturing_date: manufacturingDate,
      opening_stock: openingStock,
      brand: selectedBrand?.value,
      category: selectedCategory?.value,
      supplier: selectedSupplier?.value,
    };

    console.log('Submitting product data:', productData); // Debugging line

    try {
      // Update existing product
      await axios.put(`${baseUrl}store/products/${product.id}/`, productData);
      fetchProducts(); // Refresh the product list
      setShowModal(false); // Close the modal
    } catch (error) {
      console.error('Error updating product:', error.response?.data || error.message); // Improved error logging
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative bg-white w-full max-w-3xl mx-4 md:mx-0 md:w-3/4 lg:w-2/3 xl:w-1/2 shadow-lg rounded-lg overflow-hidden mt-20">
        <button
          className="absolute top-3 right-3 text-gray-600 hover:text-gray-900"
          onClick={() => setShowModal(false)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="p-6">
          <h2 className="text-2xl font-bold mb-6 text-center">Edit Product</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Code</label>
                <input
                  type="text"
                  value={productCode}
                  onChange={(e) => setProductCode(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  readOnly // Read-only since we're editing
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Purchase Date</label>
                <input
                  type="date"
                  value={purchaseDate}
                  onChange={(e) => setPurchaseDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                <input
                  type="date"
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Manufacturing Date</label>
                <input
                  type="date"
                  value={manufacturingDate}
                  onChange={(e) => setManufacturingDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Opening Stock</label>
                <input
                  type="number"
                  value={openingStock}
                  onChange={(e) => setOpeningStock(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Brand</label>
                <Select
                  value={selectedBrand}
                  onChange={setSelectedBrand}
                  options={brands}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <Select
                  value={selectedCategory}
                  onChange={setSelectedCategory}
                  options={categories}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Supplier</label>
                <Select
                  value={selectedSupplier}
                  onChange={setSelectedSupplier}
                  options={suppliers}
                  className="mt-1 block w-full"
                  isSearchable
                />
              </div>
            </div>
            <div className="text-center">
              <button
                type="submit"
                className="inline-flex justify-center px-4 py-2 text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700"
              >
                Update Product
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductEditForm;
