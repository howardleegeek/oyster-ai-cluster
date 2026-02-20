module.exports = {
  api: {
    input: 'https://puffy-dev-2wkdas1.getpuffy.ai/papidoc/openapi.json',
    output: {
      target: './src/types/api/',
      client: 'react-query',
      mode: 'tags-split',
      mock: true,
      prettier: true,
      clean: true,

      override: {
        mutator: {
          path: './src/lib/custom-instance.ts',
          name: 'customInstance'
        },
        query: {
          useQuery: true,
          useMutation: true,
          useInfiniteQuery: false,
          signal: true
        },
      }
    }
  }
}