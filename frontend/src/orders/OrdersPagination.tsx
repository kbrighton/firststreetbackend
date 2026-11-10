import type { MouseEvent } from 'react';
import { Pagination } from 'react-bootstrap';

type OrdersPaginationProps = {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
};

export function OrdersPagination({ page, pages, onPageChange }: OrdersPaginationProps) {
  if (pages <= 1) return null;

  const changePage = (event: MouseEvent<HTMLElement>, targetPage: number) => {
    event.preventDefault();
    if (targetPage >= 1 && targetPage <= pages && targetPage !== page) {
      onPageChange(targetPage);
    }
  };

  return (
    <nav aria-label="Search results pages">
      <Pagination>
        <Pagination.First
          aria-label="First"
          disabled={page <= 1}
          onClick={(event) => changePage(event, 1)}
        />
        <Pagination.Prev
          aria-label="Previous"
          disabled={page <= 1}
          onClick={(event) => changePage(event, page - 1)}
        />
        {Array.from({ length: pages }, (_, index) => index + 1).map((pageNumber) => (
          <Pagination.Item
            key={pageNumber}
            active={pageNumber === page}
            onClick={(event) => changePage(event, pageNumber)}
          >
            {pageNumber}
          </Pagination.Item>
        ))}
        <Pagination.Next
          aria-label="Next"
          disabled={page >= pages}
          onClick={(event) => changePage(event, page + 1)}
        />
        <Pagination.Last
          aria-label="Last"
          disabled={page >= pages}
          onClick={(event) => changePage(event, pages)}
        />
      </Pagination>
    </nav>
  );
}
