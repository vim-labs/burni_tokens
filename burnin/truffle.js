module.exports = {
  networks: {
    development: {
      host: "localhost",
      port: 8545,
      gas: 4600000,
      network_id: "*"
    },
    compilers: {
      solc: {
        version: "^0.5.0"
      }
    }
  }
};
